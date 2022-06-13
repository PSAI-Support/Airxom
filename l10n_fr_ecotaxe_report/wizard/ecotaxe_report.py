# -*- coding: utf-8 -*-

import base64
import csv
import io

from odoo import models, fields, api
from odoo.exceptions import UserError


class EcotaxeReport(models.TransientModel):
    _name = 'ecotaxe.report'
    _description = 'Rapport ecotaxe'

    date_from = fields.Date('À partir de', required=True)
    date_to = fields.Date('juste qu\'à', required=True)
    line_ids = fields.One2many('ecotaxe.report.line', 'report_id', compute='_compute_line_ids', store=True)

    @api.depends('date_from', 'date_to')
    def _compute_line_ids(self):
        stock_lines = self.env['stock.move'].search([
            ('picking_id.picking_type_id.code', '=', 'outgoing'),
            ('product_id.ecotaxe_classification_id', '!=', False),
            ('state', '=', 'done'),
            ('date', '>=', self.date_from),
            ('date', '<=', self.date_to),
        ])
        grouped_products = dict()
        for line in stock_lines:
            product = line.product_id
            code = product.default_code
            if code not in grouped_products:
                ecotaxe = product.ecotaxe_classification_id
                grouped_products[code] = {
                    'category': ecotaxe.account_ecotaxe_categ_id.code,
                    'function': ecotaxe.code,
                    'product_code': product.hs_code_id.local_code,
                    'material': ecotaxe.ecotaxe_scale_code,
                    'product_qty': 0,
                    'weight': product.weight,
                    'product_id': product.id,
                    'picking_id': line.picking_id.id,
                    'invoice_ids': []
                }
            order = line.picking_id.sale_id
            if order and order.invoice_ids:
                grouped_products[code]['invoice_ids'] += [(4, inv.id) for inv in order.invoice_ids.filtered(lambda inv: inv.state != 'draft')]
            grouped_products[code]['product_qty'] += 1
        self.line_ids = [(5,)]
        self.line_ids = [(0, 0, values) for _, values in grouped_products.items() if len(values['invoice_ids']) > 0]

    def _get_file_content(self):
        if not self.line_ids:
            raise UserError('Aucun élément à exporter')
        file = io.StringIO()
        writer = csv.writer(file, delimiter=';')
        writer.writerow([
            'Catégorie du décret à laquelle appartient le produit (cf liste des Catégories)',
            'Fonction du décret à laquelle appartient  le produit (cf liste des fonctions)',
            'Produit (Code S.H.)',
            'Code article',
            'Libellé article',
            'Matériau majoritaire du produit > à 50% du poids net (cf. liste des matériaux)',
            'total unités totales vendues',
            'Poids unitaire kg',
            'Clients',
            'Factures',
        ])
        for line in self.line_ids:
            writer.writerow([
                line.category,
                line.function,
                line.product_code,
                line.product_id.default_code,
                line.product_id.name,
                line.material,
                line.product_qty,
                line.weight,
                ', '.join(line.partner_ids.mapped('display_name')),
                ', '.join(line.invoice_ids.mapped('name'))
            ])
        file.seek(0)
        return file.read().encode('utf8')

    def action_download(self):
        self.ensure_one()
        content = self._get_file_content()
        attachment = self.env['ir.attachment'].sudo().create({
            'name': 'Rapport ecotaxe.csv',
            'datas': base64.b64encode(content),
            'res_model': self._name,
            'res_id': self.id,
        })

        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s' % attachment.id,
            'target': 'self',
        }


class EcotaxeReportLine(models.TransientModel):
    _name = 'ecotaxe.report.line'
    _description = 'Ligne rapport ecotaxe'

    report_id = fields.Many2one('ecotaxe.report', required=True)
    category = fields.Char('Catégorie du décret à laquelle appartient le produit (cf liste des Catégories)')
    function = fields.Char('Fonction du décret à laquelle appartient  le produit (cf liste des fonctions)')
    product_code = fields.Char('Produit')
    material = fields.Char('Matériau majoritaire du produit > à 50% du poids net (cf. liste des matériaux)')
    product_qty = fields.Float('total unités totales vendues')
    weight = fields.Float('Poids unitaire kg')
    picking_id = fields.Many2one('stock.picking')
    invoice_ids = fields.Many2many('account.move', string='Factures')
    product_id = fields.Many2one('product.product', string='Article')
    partner_ids = fields.Many2many('res.partner', compute='_compute_partner_ids', string='Clients')

    @api.depends('invoice_ids')
    def _compute_partner_ids(self):
        for line in self:
            line.partner_ids = [(6, 0, line.invoice_ids.mapped('partner_id').ids)]
