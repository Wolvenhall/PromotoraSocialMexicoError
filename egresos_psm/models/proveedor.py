from odoo import models, api, _, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'
    parte_relacionada = fields.Selection(selection=[('si', 'Sí'), ('no', 'No'), ], string=_('Parte Relacionada'))
