from odoo import models, api, _, fields
from datetime import date
from datetime import datetime


class HrContract(models.Model):
    _inherit = "account.move"

    @api.onchange('date', 'invoice_date')
    def _clave_vobo_transferencia(self):
        if self.date:
            fecha = self.date.strftime('%Y,%m,%d')
            fecha = datetime.strptime(fecha, '%Y,%m,%d').strftime('%Y,%m,%d')
            d = fecha.split(',')
            numero_semana = str(date(int(d[0]), int(d[1]), int(d[2])).isocalendar()[1])
            anio = str(self.date.year)
            clave_vobo = anio + ' - ' + numero_semana
            self.vobo_transferencias = clave_vobo

    @api.onchange('partner_id')
    def _es_parte_relacionada(self):
        if self.partner_id:
            categoria = self.partner_id.category_id.name
            self.parte_relacionada = categoria == 'Parte Relacionada' and 'Sí' or 'No'

    parte_relacionada = fields.Char(string='Es Parte Relacionada', readonly=True)

    solicitante = fields.Many2one('hr.employee', string='Solicitante', help="Solicitante del pago")
    direccion = fields.Many2one('hr.department', string='Dirección')
    departamento = fields.Many2one('hr.department', string='Departamento')

    vehiculo = fields.Selection(selection=[('donativo', 'Donativo'),
                                           ('financiamiento', 'Financiamiento'),
                                           ('inversion', 'Inversión'),
                                           ('pago_proveedor', 'Pago a Proveedor'),
                                           ('patrocinio', 'Patrocinio')],
                                string=_('Vehículo'))

    tipo_de_gasto = fields.Selection(selection=[('fijo', 'Gasto Fijo'),
                                                ('variable', 'Gasto Variable'), ],
                                     string=_('Tipo de gasto'))

    subtipo_de_gasto = fields.Selection(selection=[('administracion', 'Gastos de Adminstración'),
                                                   ('personal', 'Gastos de Personal'),
                                                   ('operacion', 'Gastos de Operación'),
                                                   ('inversion', 'Inversión Social'), ],
                                        string=_('Subtipo de gasto'))

    autorizacion = fields.Selection(selection=[('corporativo', 'Corporativo'), ('consejo', 'Consejo'), ], string=_('Medio de autorización'))

    deal_unico = fields.Selection(selection=[('si', 'Sí'), ('no', 'No'), ], string=_('Deal único'))
    sector = fields.Many2one('account.move.sector', 'Sector')
    subsector = fields.Many2one('account.move.subsector', 'Subsector')

    anticipo = fields.Float('Anticipo (%)')
    tipo_de_cambio = fields.Float('Tipo de cambio', digits=(12, 4))
    forma_de_pago = fields.Many2one('account.move.forma.de.pago', string='Forma de pago')
    metodo_de_pago = fields.Selection(selection=[('ppd', 'PPD'), ('pue', 'PUE'), ], string=_('Método de pago'))
    tipo_de_comprobante = fields.Many2one('account.move.tipo.comprobante', string="Tipo de comprobante")
    vobo_transferencias = fields.Char(string="VoBo Transferecias", readonly=True)
    centro_de_costos = fields.Many2one('account.move.centro.de.costos', 'Centro de costos')
    ejercicio_presupuestal = fields.Integer(string="Ejercicio Presupuestal")
    nombre_del_proyecto = fields.Many2one('proyecto', 'Nombre del proyecto')

    # SALESFORCE
    estado_sincronizacion = fields.Text(string="Estado", readonly=True)
    fecha_sincronizacion = fields.Datetime(string='Fecha', readonly=True, help="Fecha de sincronización con salesforce")

    sistema_origen = fields.Char(string="Sistema origen")
