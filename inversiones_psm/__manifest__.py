# -*- coding: utf-8 -*-
{
    'name': "Inversiones PSM",

    'summary': """Inversiones Promotora Socia México""",

    'description': """Inversiones Promotora Socia México""",
    "category": "Tools",
    'author': "Wolvenhall",
    'website': "http://www.wolvenhall.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'account', 'egresos_psm'],
    "data": [
        "security/ir.model.access.csv",
        "views/inversiones_css_javascript.xml",
        "views/cedula_asociadas.xml",
        "views/cedula_acciones.xml",
        "views/cedula_fondos.xml",
        "views/creditos_beneficiarios.xml",
        "views/creditos_amortizacion.xml",
        "views/creditos_disposicion.xml",
        "views/control_de_creditos.xml",
    ],
    "test": [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
