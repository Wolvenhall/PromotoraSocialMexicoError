from odoo import models, fields, api, _


class LineasDeCreditos(models.Model):
    _name = 'inversiones.credito.linea'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'linea_de_credito'
    _description = 'Línea de Crédito'

    @api.onchange('beneficiario')
    def _es_parte_relacionada(self):
        if self.beneficiario:
            categoria = self.beneficiario.category_id.name
            self.parte_relacionada = categoria == 'Parte Relacionada' and 'Sí' or 'No'

    def _beneficiario_id(self):
        context = self.env.context.get('params')
        if context:
            id_beneficiario = context.get('id')
            if id_beneficiario:
                return id_beneficiario

    # def obten_total_disposiciones(self):
    #     total = self.env['inversiones.credito.disposicion'].search_count([('linea_de_credito', '=', self.id)])
    #     self.conteo_disposiciones = total
    #
    # def muestra_disposiciones(self):
    #     return {
    #         'name': _('Disposiciones'),
    #         'domain': [('linea_de_credito', '=', self.id)],
    #         'view_type': 'form',
    #         'res_model': 'inversiones.credito.disposicion',
    #         'view_id': False,
    #         'view_mode': 'tree,form',
    #         'type': 'ir.actions.act_window',
    #     }

    linea_de_credito = fields.Char(string='Línea de crédito', required=True, copy=False)
    beneficiario_id = fields.Many2one('inversion.control.credito', "Beneficiario", default=_beneficiario_id, store=True, redonly=True)
    parte_relacionada = fields.Char(string='Es Parte Relacionada', store=True, readonly=True)
    contrato = fields.Binary(string="Contrato")
    sector = fields.Many2one('account.move.sector', string='Sector', required=True)
    devengo = fields.Many2one('inversion.credito.devengo', string='Devengo de Intereses', required=True)
    tipo = fields.Many2one('inversion.credito.tipo', string='Tipo de crédito', required=True)
    monto_autorizado = fields.Float(string='Monto autorizado', digits=(12, 2))
    tasa_de_interes = fields.Char(string='Tasa de Interes')
    vigencia_credito_inicio = fields.Date(string='Vigencia inicio')
    vigencia_credito_fin = fields.Date(string='Vigencia fin')
    periodo_de_gracia = fields.Date(string='Periodo de gracia')
    forma_de_pago = fields.Integer(string='Forma de pago')
    es_pago_fijo = fields.Selection(selection=[('si', 'Sí'), ('no', 'No')], string=_('Es Pago Fijo'))
    monto_pago_fijo = fields.Float(string='Monto pago fijo', digits=(12, 2))
    tipo_de_moneda = fields.Selection(selection=[('mxn', 'MXN'), ('usd', 'USD')], string=_('Tipo de Moneda'))
    estatus = fields.Selection(selection=[('vigente', 'Vigente'),
                                          ('no_vigente', 'No Vigente'),
                                          ('linea_agotada', 'Línea agotada'),
                                          ('capitalizado', 'Capitalizado')],
                               string=_('Estatus'))
    # conteo_disposiciones = fields.Integer(string="Disposiciones", compute="obten_total_disposiciones")
    dispocisiones = fields.Many2many('inversion.credito.disposicion', relation='credito_disposicion_rel', string="Disposiciones")



