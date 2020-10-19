# -*- coding: utf-8 -*-

from odoo import fields, models, _


class Proveedor(models.Model):
    _inherit = 'res.partner'

    parte_relacionada = fields.Selection(selection=[('si', 'Sí'),
                                                    ('no', 'No'), ],
                                         string='Parte Relacionada')
