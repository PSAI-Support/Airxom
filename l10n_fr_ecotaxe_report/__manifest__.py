# -*- coding: utf-8 -*-
{
    'name': "l10n_fr_ecotaxe_report",

    'summary': 'Rapport écotaxe',

    'description': """
    """,

    'author': "EaSI",
    'website': "https://easi-soft.fr/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',
    'price': 50.00,
    'currency': "EUR",
    # any module necessary for this one to work correctly
    'depends': [
        'account',
        'stock',
        'l10n_fr_ecotaxe',
        'l10n_fr_intrastat_product',
    ],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizard/ecotaxe_report_views.xml'
    ],
}
