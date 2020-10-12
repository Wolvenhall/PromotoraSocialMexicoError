# -*- coding: utf-8 -*-
{
    'name': "Evaluaciones PSM",

    'summary': """Evaluaciones Promotora Socia México""",

    'description': """Evaluaciones Promotora Socia México""",
    "category": "Tools",
    'version': '1.1',
    'author': "Wolvenhall",
    'website': "http://www.wolvenhall.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'survey'],
    "data": [
        "security/ir.model.access.csv",
        "views/red_de_evaluaciones.xml",
        "views/red_del_colaborador.xml",
    ],
    "test": [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
