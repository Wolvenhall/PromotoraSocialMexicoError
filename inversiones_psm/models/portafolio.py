from odoo import models, fields, api, _


class Portafolio(models.Model):
    _name = 'inversion.portafolio'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'beneficiario'
    _description = "Portafolio"

    # ---------------------------------------------------------------------------------------
    # BOTON INTELIGENTE ACCIONES
    # ---------------------------------------------------------------------------------------

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

    # ---------------------------------------------------------------------------------------
    # BOTON INTELIGENTE FONDOS
    # ---------------------------------------------------------------------------------------

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

    # ---------------------------------------------------------------------------------------
    # BOTON INTELIGENTE LINEAS DE CREDITO
    # ---------------------------------------------------------------------------------------

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

    # ---------------------------------------------------------------------------------------
    # FUNCIONES
    # ---------------------------------------------------------------------------------------

    def _total_monto_invertido_acciones(self):
        for record in self:
            total = 0
            acciones = self.env['inversion.cedula.accion'].search([('asociada_id', '=', record.id)])
            if acciones:
                for inversion in acciones:
                    monto_invertido_psm = inversion.monto_invertido_psm
                    total = monto_invertido_psm + total

            record.monto_invertido_acciones = total

    def _total_acciones_suscritas_psm(self):
        for record in self:
            total = 0
            acciones = self.env['inversion.cedula.accion'].search([('asociada_id', '=', record.id)])
            if acciones:
                for inversion in acciones:
                    acciones_suscritas_psm = inversion.acciones_suscritas_psm
                    total = acciones_suscritas_psm + total

            record.acciones_suscritas_psm = total

    def _total_porcentaje_de_participacion(self):
        for record in self:
            porcentaje_de_participacion = 0
            acciones = self.env['inversion.cedula.accion'].search([('asociada_id', '=', record.id)], order='id desc', limit=1)
            if acciones:
                porcentaje_de_participacion = acciones.porcentaje_de_participacion
            record.porcentaje_de_participacion = porcentaje_de_participacion

    # ---------------------------------------------------------------------------------------
    # CAMPOS
    # ---------------------------------------------------------------------------------------

    beneficiario = fields.Many2one('res.partner', string='Beneficiario', required=True)
    parte_relacionada = fields.Char(string='Es Parte Relacionada', store=True, readonly=True)
    conteo_acciones = fields.Integer(string="Acciones", compute="obten_total_acciones")
    conteo_fondos = fields.Integer(string="Fondos", compute="obten_total_fondos")
    conteo_lineas_credito = fields.Integer(string="Creditos", compute="obten_total_creditos")

    monto_invertido_acciones = fields.Float(string="Monto Invertido", compute="_total_monto_invertido_acciones")
    acciones_suscritas_psm = fields.Integer(string="Acciones Suscritas", compute="_total_acciones_suscritas_psm")
    porcentaje_de_participacion = fields.Float(string="% Participación", digits=(12, 4), compute="_total_porcentaje_de_participacion")

