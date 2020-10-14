# -*- coding: utf-8 -*-
{
    'name': "Evaluaciones PSM",

    'summary': """Evaluaciones Promotora Socia México""",

    'description': """Evaluaciones Promotora Socia México""",
    "category": "Human Resources",
    'version': '13.1.3',
    'author': "Wolvenhall",
    'website': "http://www.wolvenhall.com",
    'maintainer': "Wolvenhall",
    'support': "Wolvenhall",

    'depends': ['base', 'hr', 'survey'],
    "data": [
        "security/ir.model.access.csv",
        "views/red_de_evaluaciones.xml",
        "views/red_del_colaborador.xml",
    ],
    "test": [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
