# -*- coding: utf-8 -*-
{
    'name': "Partida de egresos PSM",

    'summary': """Partida de egresos Promotora Socia México""",

    'description': """Partida de egresos Promotora Socia México""",
    "category": "Tools",
    'author': "Wolvenhall",
    'website': "http://www.wolvenhall.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'account_accountant'],
    "data": [
        "security/ir.model.access.csv",
        "views/factura_de_proveedor.xml",
        "views/sector.xml",
        "views/subsector.xml",
        "views/proyecto.xml",
        "views/centrodecostos.xml",
        "views/partida_de_egresos.xml"
    ],
    "test": [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
