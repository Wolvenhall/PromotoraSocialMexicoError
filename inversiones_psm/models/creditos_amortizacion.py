from odoo import models, fields, api, _


class TablaDeAmortizacion(models.Model):
    _name = 'inversion.credito.amortizacion'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'numero'
    _description = 'Tabla de Amortización'

    disposicion = fields.Many2one('inversion.credito.disposicion', string='Disposición')
    numero = fields.Integer(string='Número')
    fecha_de_pago = fields.Date(string='Fecha de pago')
    tasa_interes_anual = fields.Float(string='Tasa de Interes Anual', digits=(12, 4))

    ministraciones = fields.Float(string='Ministraciones', digits=(12, 2))
    saldo_insoluto = fields.Float(string='Saldo insoluto', digits=(12, 2))
    amortizacion_de_capital = fields.Float(string='Amortizacion de capital', digits=(12, 2))
    intereses_devengados = fields.Float(string='Interes devengado del periodo', digits=(12, 2))
    iva = fields.Float(string='IVA', digits=(12, 2))
    valor_factura = fields.Float(string='Valor factura', digits=(12, 2))
    total_a_pagar = fields.Float(string='Total a pagar del periodo', digits=(12, 2))
    adeudo_intereses = fields.Float(string='Adeudo intereses', digits=(12, 2))
    adeudo_iva = fields.Float(string='Adeudo IVA', digits=(12, 2))
    adeudo_capital = fields.Float(string='Adeudo Capital', digits=(12, 2))
    gran_total_a_pagar = fields.Float(string='GRAN TOTAL A PAGAR', digits=(12, 2))

    factura = fields.Many2one('account.move', string="Factura")
