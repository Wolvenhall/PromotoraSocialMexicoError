from odoo import models, fields, api, _


class ControlDeCreditos(models.Model):
    _name = 'inversion.control.credito'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'beneficiario'
    _description = "Control de creditos"

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

    def obten_total_creditos(self):
        total = self.env['inversiones.credito.linea'].search_count([('beneficiario_id', '=', self.beneficiario.id)])
        self.conteo_lineas_credito = total

    def muestra_creditos(self):
        return {
            'name': _('Creditos'),
            'domain': [('beneficiario_id', '=', self.beneficiario.id)],
            'view_type': 'form',
            'res_model': 'inversiones.credito.linea',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    beneficiario = fields.Many2one('res.partner', string='Beneficiario', required=True)
    parte_relacionada = fields.Char(string='Es Parte Relacionada', store=True, readonly=True)
    conteo_acciones = fields.Integer(string="Acciones", compute="obten_total_acciones")
    conteo_fondos = fields.Integer(string="Fondos", compute="obten_total_fondos")
    conteo_lineas_credito = fields.Integer(string="Creditos", compute="obten_total_creditos")

