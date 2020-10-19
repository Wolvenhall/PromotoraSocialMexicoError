from odoo import models, fields, api, _


class Disposicion(models.Model):
    _name = 'inversion.credito.disposicion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'disposicion'
    _description = 'Disposiciones'

    linea_de_credito = fields.Many2one('inversiones.credito.linea', string='Línea de Crédito')

    disposicion = fields.Char(string='Disposición', required=True, copy=False)
    factura = fields.Many2one('account.move', string="Factura")
    fecha_de_pago = fields.Date(string="Fecha de pago", related="factura.date")
    ministraciones = fields.Float(string='Ministraciones', digits=(12, 2))
    saldo_insoluto = fields.Float(string='Saldo insoluto', digits=(12, 2))
    amortizaciones = fields.Many2many('inversion.credito.amortizacion', relation='disposicion_amortizacion_rel',
                                     string="Amortizaciones")

    def action_view_form_disposicion(self):
        view = self.env.ref('inversiones_psm.credito_disposicion_form_view')
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'inversion.credito.disposicion',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'res_id': self.id,
            'context': self.env.context,
        }
