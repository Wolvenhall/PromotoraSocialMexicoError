from odoo import models, api, _, fields


class Proveedor(models.Model):
    _inherit = 'res.partner'

    parte_relacionada = fields.Boolean(string='Parte Relacionada')
