# -*- coding: utf-8 -*-
{
    'name': "Eventos PSM",

    'summary': """Eventos Promotora Socia México""",

    'description': """Eventos Promotora Socia México""",
    "category": "Tools",
    'author': "Wolvenhall",
    'website': "http://www.wolvenhall.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'approvals'],
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/lineamientos.xml",
        "views/approval_request_views.xml",
        "views/area.xml",
        "views/articulos_promocionales.xml",
        "views/audiencia.xml",
        "views/audiovisual.xml",
        "views/catering.xml",
        "views/diseno.xml",
        "views/distribucion.xml",
        "views/equipoextra.xml",
        "views/event_views.xml",
        "views/product_etiqueta.xml",
        "views/categoria.xml",
        "views/relacion.xml",
    ],
    "test": [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
