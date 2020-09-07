# -*- coding: utf-8 -*-
{
    'name': "Nomina PSM",

    'summary': """Nomina Promotora Socia México""",

    'description': """Nomina Promotora Socia México""",
    "category": "Tools",
    'author': "Wolvenhall",
    'website': "http://www.wolvenhall.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'hr_payroll',
        'hr_contract'],
    "data": [
        "security/ir.model.access.csv",
        "views/calculos_nomina.xml",
        "views/contrato_sdi.xml",
        "views/tablas_nomina.xml",
        "views/tabla_vacaciones.xml",
        "views/tabla_efectos_cotizacion.xml",
        "views/tabla_isr.xml",
        "views/tabla_subsidio_empleo.xml",        
    ],
    "test": [],
    'installable': True,
    'auto_install': False,
    'application': False,
}
