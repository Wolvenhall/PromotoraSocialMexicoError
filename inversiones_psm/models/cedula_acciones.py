from odoo import models, fields, api, _
from odoo.http import request


class Acciones(models.Model):
    _name = 'inversion.cedula.accion'
    _rec_name = 'acciones_id'
    _description = "Acciones"

    @api.onchange('acciones_capital_fijo', 'acciones_capital_variable')
    def _acciones_totales(self):
        total = self.acciones_capital_fijo + self.acciones_capital_variable
        self.acciones_totales = total

    @api.onchange('acciones_totales', 'aumento_capital_fijo', 'aumento_capital_variable')
    def _acciones_totales_final(self):
        total = self.acciones_totales + self.aumento_capital_fijo + self.aumento_capital_variable
        self.acciones_totales_final = total

    # @api.onchange('acciones_suscritas_psm')
    # def _acciones_totales_psm(self):
    #     print("no")
        # ultimo_id = self.env['inversiones.cedula.acciones'].search([('asociada_id', '=', self.asociada_id.id)], order='id desc')
        # acciones_totales_psm = 0
        # if ultimo_id:
        #     registro = self.env['inversiones.cedula.acciones'].search([('id', '=', ultimo_id)])
        #     if registro.acciones_totales_psm:
        #         acciones_totales_psm = registro.acciones_totales_psm
        #     else:
        #         acciones_totales_psm = 0
        # total = acciones_totales_psm / self.acciones_suscritas_psm
        # self.acciones_totales_psm = total

    @api.onchange('acciones_totales_final', 'acciones_totales_psm')
    def _porcentaje_de_participacion(self):

        acciones_totales_final = self.acciones_totales_final
        acciones_totales_psm = self.acciones_totales_psm
        total = 0

        if acciones_totales_final > 0 and acciones_totales_psm == 0:
            total = 0
        elif acciones_totales_psm > 0 and acciones_totales_final == 0:
            total = 0
        elif acciones_totales_final > 0 and acciones_totales_psm > 0:
            total = (acciones_totales_psm / acciones_totales_final) * 100

        self.porcentaje_de_participacion = total

    def _asociada_id(self):
        context = self.env.context.get('params')
        if context:            
            id_asociada = context.get('id')
            if id_asociada:
                return id_asociada

    def _compute_id(self):
        for i, record in enumerate(self.sorted('id', reverse=False), 1):
            record.acciones_id = i

    egreso = fields.Many2one('account.move', string='Factura')
    asociada_id = fields.Many2one('inversion.cedula.asociada', "Asociada", default=_asociada_id, store=True, redonly=True)
    acciones_id = fields.Integer(string='ID', compute=_compute_id)
    movimiento = fields.Char(string="Movimiento", required=True)
    acto = fields.Char(string="Acto")
    documento = fields.Binary(String="Documento")
    fecha_del_documento = fields.Date(string="Fecha")
    documento_legal_firmado = fields.Selection(selection=[('Sí', 'Sí'), ('No', 'No'), ('Na', 'Na')],
                                               string=_('Firmado'))
    acciones_capital_fijo = fields.Integer(string="Acciones Capital Fijo")
    acciones_capital_variable = fields.Integer(string="Acciones Capital Variable")
    acciones_totales = fields.Integer(string="Acciones Totales")

    aumento_capital_fijo = fields.Integer(string="Aumento Capital Fijo")
    aumento_capital_variable = fields.Integer(string="Aumento Capital Variable")
    acciones_totales_final = fields.Integer(string="Acciones Totales Final")

    acciones_suscritas_psm = fields.Integer(string="Acciones Suscritas PSM")
    acciones_totales_psm = fields.Integer(string="Acciones Totales PSM")

    monto_invertido_psm = fields.Integer(string="Monto Invertido por PSM")
    fecha_de_pago = fields.Date(string="Fecha de pago")
    porcentaje_de_participacion = fields.Float(string="% Participación", digits=(12, 4))

    comentarios = fields.Text(string="Comentarios")
