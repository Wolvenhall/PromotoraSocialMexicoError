from odoo import models, api, _, fields


class HrContract(models.Model):
    _inherit = "account.move"

    solicitante = fields.Many2one('hr.employee', string='Solicitante', help="Solicitante del pago")
    direccion = fields.Many2one('hr.department', string='Dirección')
    departamaneto = fields.Many2one('hr.department', string='Departamento')

    vehiculo = fields.Selection(selection=[('donativo', 'Donativo'),
                                           ('financiamiento', 'Financiamiento'),
                                           ('inversion', 'Inversión'),
                                           ('pago_proveedor', 'Pago a Proveedor'),
                                           ('patrocinio', 'Patrocinio')],
                                string=_('Vehículo'))

    tipo_de_gasto = fields.Selection(selection=[('fijo', 'Gasto Fijo'),
                                        ('variable', 'Gasto Variable'),
                                        ('inversion', 'Inversion Social'), ],
                             string=_('Tipo de gasto'))

    subtipo_de_gasto = fields.Selection(selection=[('administracion', 'Gastos de Adminstración'),
                                                ('personal', 'Gastos de Personal'),
                                                ('operacion', 'Gastos de Operación'),
                                                ('inversion', 'Inversión Social'), ],
                                     string=_('Subtipo de gasto'))

    tipo_de_aprobacion = fields.Selection(selection=[('corporativo', 'Corporativo'), ('consejo', 'Consejo'), ],
                                          string=_('Tipo de Aprobación'))
    deal_unico = fields.Selection(selection=[('si', 'Sí'), ('no', 'No'), ], string=_('Deal único'))

    sector = fields.Many2one('account.move.sector', 'Sector')
    subsector = fields.Many2one('account.move.subsector', 'Subsector')

    anticipo = fields.Float('Anticipo (%)')
    tipo_de_cambio = fields.Float('Tipo de cambio', digits=(12, 4))
    forma_de_pago = fields.Many2one('account.move.forma.de.pago', string='Forma de pago')
    metodo_de_pago = fields.Selection(selection=[('ppd', 'PPD'), ('pue', 'PUE'), ], string=_('Método de pago'))
    tipo_de_comprobante = fields.Many2one('account.move.tipo.comprobante', string="Tipo de comprobante")
    vobo_transferencias = fields.Text(string="VoBo Transferecias")
    centro_de_costos = fields.Many2one('account.move.centro.de.costos', 'Centro de costos')
    ejercicio_presupuestal = fields.Integer(string="Ejercicio Presupuestal")
    nombre_del_proyecto = fields.Many2one('proyecto', 'Nombre del proyecto')

    # SALESFORCE
    estatus_sincronizacion = fields.Text(string="Estatus de Sincronización", readonly=True)
    fecha_sincronizacion = fields.Datetime(string='Fecha de sincronización', readonly=True,
                                           help="Fecha de sincronización con salesforce")

