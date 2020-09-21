from odoo import models, api, _, fields


class HrContract(models.Model):
    _inherit = "account.move"

    solicitante = fields.Many2one('hr.employee', string='Solicitante', help="Solicitante del pago")
    direccion = fields.Many2one('hr.department', string='Dirección')
    departamaneto = fields.Many2one('hr.department', string='Departamento')
    oficina = fields.Many2one('account.move.oficina', string='Oficina')
    gasto = fields.Selection(
        selection=[('fijo', 'Gasto Fijo'),
                   ('variable', 'Gasto Variable'),
                   ('inversion', 'Inversion Social'), ],
        string=_('Gasto'))
    tipo_de_gasto = fields.Selection(
        selection=[('administracion', 'Gastos de Adminstración'),
                   ('personal', 'Gastos de Personal'),
                   ('operacion', 'Gastos de Operación'),
                   ('inversion', 'Inversión Social'), ],
        string=_('Tipo de gasto'))
    corporativo = fields.Selection(selection=[('si', 'Sí'), ('no', 'No'), ], string=_('Corporativo'))
    deal_unico = fields.Selection(selection=[('si', 'Sí'), ('no', 'No'), ], string=_('Deal único'))
    vehiculo = fields.Selection(
        selection=[('donativo', 'Donativo'),
                   ('patrocinio', 'Patrocinio'),
                   ('inversion', 'Inversión'),
                   ('financiamiento', 'Financiamiento'), ],
        string=_('Vehículo'))
    sector = fields.Many2one('account.move.sector', 'Sector')
    subsector = fields.Many2one('account.move.subsector', 'Subsector')
    anticipo = fields.Float('Anticipo (%)')
    tipo_de_cambio = fields.Float('Tipo de cambio', digits=(12, 4))
    forma_de_pago = fields.Many2one('account.move.forma.de.pago', string='Forma de pago')
    metodo_de_pago = fields.Selection(selection=[('ppd', 'PPD'), ('pue', 'PUE'), ], string=_('Método de pago'))
    tipo_de_comprobante = fields.Many2one('account.move.tipo.comprobante', string="Tipo de comprobante")
    numero_de_cheque = fields.Text(string="Número de cheque")
    cheque_entregado = fields.Date(string="Cheque entregado")
    poliza_entregada = fields.Date(string="Póliza entregada")
    entrega_de_poliza = fields.Text(string="Entrega de póliza")
    numero_de_recibo = fields.Text(string="Número de cheque")
    vobo_transferencias = fields.Text(string="VoBo Transferecias")
    centro_de_costos = fields.Many2one('account.move.centro.de.costos', 'Sector')
    partida_presupuestal = fields.Text(string="Partida Presupuestal")
    ejercicio_presupuestal = fields.Integer(string="Ejercicio Presupuestal")
    nombre_del_proyecto = fields.Many2one('proyecto', 'Nombre del proyecto')
    estatus_sincronizacion = fields.Text(string="Estatus de Sincronización", readonly=True)
    fecha_sincronizacion = fields.Datetime(string='Fecha de sincronización', readonly=True,
                                           help="Fecha de sincronización con salesforce")
