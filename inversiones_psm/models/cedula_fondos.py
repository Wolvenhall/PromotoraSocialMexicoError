from odoo import models, fields, api, _


class Fondos(models.Model):
    _name = 'inversion.cedula.fondo'
    _rec_name = 'fondos_id'
    _description = "Fondos"

    # @api.depends('acciones_capital_variable')
    # def _monto_invertido_por_psm_mxn(self):
    #     total = self.monto_transferido_por_psm_usd * self.tipo_de_cambio
    #     self.monto_invertido_por_psm_mxn = total
    #
    # @api.depends('acciones_capital_variable')
    # def _porcentaje_de_participacion(self):
    #     total = self.acciones_totales + self.aumento_capital_fijo + self.aumento_capital_variable
    #     self.porcentaje_de_participacion = total

    egreso = fields.Many2one('account.move', string='Registro de egreso')
    asociada_id = fields.Many2one('inversion.cedula.asociada', "Asociada")
    fondos_id = fields.Integer(string='ID')
    movimiento = fields.Char(string="Movimiento")
    acto = fields.Char(string="Acto")
    fecha = fields.Date(string="Fecha")

    capital_total_comprometido = fields.Float(string="Capital Total Comprometido", digits=(12, 2))
    capital_comprometido_psm = fields.Float(string="Capital Total Comprometido", digits=(12, 2))
    capital_call_psm_usd = fields.Float(string="Capital Call PSM en USD", digits=(12, 2))
    monto_transferido_por_psm_usd = fields.Float(string="Monto Transferido por PSM en USD", digits=(12, 2))
    tipo_de_cambio = fields.Float(string="Capital Total Comprometido", digits=(12, 2))

    monto_invertido_por_psm_mxn = fields.Float(string="Monto Transferido por PSM en USD", digits=(12, 2))
    fechadepago = fields.Date(string="Fecha de pago")
    porcentaje_de_participacion = fields.Float(string="% De Participación")

    comentarios = fields.Text(string="Comentarios")
