# © 2014-2016 Akretion (http://www.akretion.com)
#   @author Mourad EL HADJ MIMOUNE <mourad.elhadj.mimoune@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.tools.misc import formatLang


class AccountMove(models.Model):
    _inherit = "account.move"

    amount_ecotaxe = fields.Monetary(
        string="Included Ecotaxe", store=True, compute="_compute_ecotaxe"
    )
    amount_without_ecotaxe = fields.Monetary('Hors ecotaxe', store=True, compute='_compute_amount_without_ecotaxe')

    @api.depends("invoice_line_ids.subtotal_ecotaxe")
    def _compute_ecotaxe(self):
        for move in self:
            move.amount_ecotaxe = sum(move.line_ids.mapped("subtotal_ecotaxe"))

    @api.depends('amount_ecotaxe', 'amount_untaxed')
    def _compute_amount_without_ecotaxe(self):
        for move in self:
            move.amount_without_ecotaxe = move.amount_untaxed - move.amount_ecotaxe

    # @api.model
    # def _get_tax_totals(
    #         self, partner, tax_lines_data, amount_total, amount_untaxed, currency
    # ):
    #     """Include Ecotax when this method is called upon a single invoice
    #
    #     NB: `_get_tax_totals()` is called when field `tax_totals_json` is
    #     computed, which is used in invoice form view to display taxes and
    #     totals.
    #     """
    #     res = super()._get_tax_totals(
    #         partner, tax_lines_data, amount_total, amount_untaxed, currency
    #     )
    #     if len(self) != 1:
    #         return res
    #
    #     env = self.with_context(lang=partner.lang).env
    #     amount_untaxed = self.amount_untaxed
    #     amount_untaxed_amt = formatLang(env, amount_untaxed, currency_obj=currency)
    #     ecotaxe_tax_line_data = list(filter(lambda x: x['tax'].amount_type == 'code', tax_lines_data))
    #     if not ecotaxe_tax_line_data:
    #         return res
    #     ecotaxe_tax_line_data = ecotaxe_tax_line_data[0]
    #     ecotaxe_subtotal = list(filter(lambda x: x['tax_group_id'] == ecotaxe_tax_line_data['tax'].tax_group_id.id, res['groups_by_subtotal'][_("Untaxed Amount")]))
    #     if not ecotaxe_subtotal:
    #         return res
    #     ecotaxe_subtotal = ecotaxe_subtotal[0]['tax_group_amount'] + self.amount_untaxed
    #     ecotaxe_subtotal_amt = formatLang(env, ecotaxe_subtotal, currency_obj=currency)
    #     data = list(res["groups_by_subtotal"].get(_("Untaxed Amount")) or [])
    #     data.insert(1, {
    #         "tax_group_name": "Total net dont ECO",
    #         "tax_group_amount": ecotaxe_subtotal,
    #         "formatted_tax_group_amount": ecotaxe_subtotal_amt,
    #         "tax_group_base_amount": amount_untaxed,
    #         "formatted_tax_group_base_amount": amount_untaxed_amt,
    #         "tax_group_id": False,  # Not an actual tax
    #         "group_key": "Hors ecotaxe",
    #     })
    #     res["groups_by_subtotal"][_("Untaxed Amount")] = data
    #     return res
