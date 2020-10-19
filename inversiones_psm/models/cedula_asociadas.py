from odoo import models, fields, api, _


class Asociada(models.Model):
    _name = 'inversion.cedula.asociada'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'asociada'
    _description = "Asociada"

    def obten_total_acciones(self):
        total = self.env['inversion.cedula.accion'].search_count([('asociada_id', '=', self.id)])
        self.conteo_acciones = total

    def muestra_acciones(self):
        return {
            'name': _('Acciones'),
            'domain': [('asociada_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'inversion.cedula.accion',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def obten_total_fondos(self):
        total = self.env['inversion.cedula.fondo'].search_count([('asociada_id', '=', self.id)])
        self.conteo_fondos = total

    def muestra_fondos(self):
        return {
            'name': _('Fondos'),
            'domain': [('fondos_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'inversion.cedula.fondo',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    asociada = fields.Many2one('res.partner', string='Asociada', required=True)
    acciones_id = fields.Many2many('inversion.cedula.accion', string='Acciones')
    fondos_id = fields.Many2many('inversion.cedula.fondo', string='Fondos')
    conteo_acciones = fields.Integer(string="Acciones", compute="obten_total_acciones")
    conteo_fondos = fields.Integer(string="Fondos", compute="obten_total_fondos")

