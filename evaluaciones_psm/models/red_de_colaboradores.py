from odoo import models, fields, api, _


class RedDelColaborador(models.Model):
    _name = 'red.del.colaborador'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'colaborador'
    _description = "Mapeo del Colaborador"

    def action_draft(self):
        for rec in self:
            rec.state = 'draft'

    def action_process(self):
        for rec in self:
            rec.state = 'process'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    red_de_evaluacion = fields.Many2one('red.de.evaluaciones', string='Red de evaluación', readonly=True)
    colaborador = fields.Many2one('hr.employee', string='A evaluar')

    jefes = fields.Many2many('hr.employee', relation="red_jefe_rel", string='Jefe')
    reportes_directos = fields.Many2many('hr.employee', relation="red_reporte_rel", string='Reportes Directos')
    pares = fields.Many2many('hr.employee', relation="red_par_rel", string='Pares')
    clientes_internos = fields.Many2many('hr.employee', relation="red_cliente_interno_rel", string='Clientes Internos')

    state = fields.Selection([
        ('draft', 'Borrador'),
        ('process', 'En proceso'),
        ('done', 'Terminado'),
    ], string='Estado', tracking=True, default='draft', index=True, readonly=True)








