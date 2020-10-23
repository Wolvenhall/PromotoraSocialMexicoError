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

    def _asociada_id(self):
        id_asociada = self.env.context.get('active_id')
        if id_asociada:
            return id_asociada

    def _compute_id(self):
        for i, record in enumerate(self.sorted('acciones_id', reverse=False), 1):
            record.acciones_id = i
            self.acciones_id = i

    def _calculo_acciones_capital_fijo(self):
        accion_anterior = self._accion_anterior()
        if accion_anterior:
            acciones_capital_fijo = accion_anterior.acciones_capital_fijo + accion_anterior.aumento_capital_fijo
            return acciones_capital_fijo

    def _accion_anterior(self):
        id_asociada = self.env.context.get('active_id')
        if id_asociada:
            acciones_asociada = self.env['inversion.cedula.accion'].search([('asociada_id', '=', id_asociada)], order='id desc', limit=1)
            if acciones_asociada:
                if acciones_asociada.acciones_id > 0:
                    accion_anterior = self.env['inversion.cedula.accion'].search([('asociada_id', '=', id_asociada), ('acciones_id', '=', acciones_asociada.acciones_id)])
                    return accion_anterior

    # ---------------------------------------------------------------------------------------
    # CAMPOS DEL MODELO
    # ---------------------------------------------------------------------------------------

    egreso = fields.Many2one('account.move', string='Factura')
    asociada_id = fields.Many2one('inversion.portafolio', "Beneficiario", default=_asociada_id, store=True, redonly=True)
    acciones_id = fields.Integer(string='ID', default=_compute_id, store=True, readonly=True)
    movimiento = fields.Char(string="Movimiento", required=True)
    acto = fields.Char(string="Acto")
    documento = fields.Binary(String="Documento")
    fecha_del_documento = fields.Date(string="Fecha")
    documento_legal_firmado = fields.Selection(selection=[('Sí', 'Sí'), ('No', 'No'), ('Na', 'Na')], string=_('Firmado'))

    acciones_capital_fijo = fields.Integer(string="Acciones Capital Fijo", default=_calculo_acciones_capital_fijo, store=True)
    acciones_capital_variable = fields.Integer(string="Acciones Capital Variable")
    acciones_totales = fields.Integer(string="Acciones Totales")

    aumento_capital_fijo = fields.Integer(string="Aumento Capital Fijo")
    aumento_capital_variable = fields.Integer(string="Aumento Capital Variable")
    acciones_totales_final = fields.Integer(string="Acciones Totales Final")

    acciones_suscritas_psm = fields.Integer(string="Acciones Suscritas PSM")
    acciones_totales_psm = fields.Integer(string="Acciones Totales PSM")

    monto_invertido_psm = fields.Float(string="Monto Invertido por PSM")
    fecha_de_pago = fields.Date(string="Fecha de pago")
    porcentaje_de_participacion = fields.Float(string="% Participación", digits=(12, 4))

    comentarios = fields.Text(string="Comentarios")

    # ---------------------------------------------------------------------------------------
    # VALORES CALCULADOS AL GUARDAR REGISTRO
    # ---------------------------------------------------------------------------------------

    def _obtener_ultimo_id(self):
        id_asociada = self.env.context.get('active_id')
        id_accion = 0
        if id_asociada:
            ultima_accion = self.env['inversion.cedula.accion'].search([('asociada_id', '=', id_asociada)], order='id desc', limit=1)
            if ultima_accion:
                id_accion = ultima_accion.acciones_id + 1
            else:
            id_accion = 0
            
        return id_accion

    def _acciones_totales_psm_VACIA(self):
        acciones_totales_psm = 0

        accion_anterior = self._accion_anterior()

        if accion_anterior:

            if accion_anterior.acciones_totales_psm > 0:
                acciones_totales_psm = accion_anterior.acciones_totales_psm
        return acciones_totales_psm

    def _acciones_totales_final_valor(self):
        total = self.acciones_totales + self.aumento_capital_fijo + self.aumento_capital_variable
        return total

    def _acciones_totales_psm(self, acciones_suscritas_psm):
        total = 0
        accion_anterior = self._accion_anterior()
        if accion_anterior:
            acciones_totales_psm = accion_anterior.acciones_totales_psm
            total = acciones_totales_psm + acciones_suscritas_psm

        return total

    def _porcentaje_de_participacion(self, acciones_totales_final,  acciones_totales_psm):
        total = 0
        if acciones_totales_final > 0 and acciones_totales_psm == 0:
            total = 0
        elif acciones_totales_psm > 0 and acciones_totales_final == 0:
            total = 0
        elif acciones_totales_final > 0 and acciones_totales_psm > 0:
            total = (acciones_totales_psm / acciones_totales_final) * 100
        return total

    @api.model
    def create(self, vals):
        vals['acciones_totales_psm'] = self._acciones_totales_psm(vals['acciones_suscritas_psm'])
        vals['porcentaje_de_participacion'] = self._porcentaje_de_participacion(vals['acciones_totales_final'], vals['acciones_totales_psm'])
        vals['acciones_id'] = self._obtener_ultimo_id()
        return super(Acciones, self).create(vals)
