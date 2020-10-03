from odoo import models, fields, api, _


class RedDelColaborador(models.Model):
    _name = 'red.del.colaborador'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'colaborador'
    _description = "Red del Colaborador"

    red_de_evaluacion = fields.Many2one('red.de.evaluaciones', string='Red de evaluación')
    colaborador = fields.Many2one('hr.employee', string='A evaluar', readonly=True)
    
    jefes = fields.Many2many('hr.employee', relation="red_jefe_rel", string='Jefe')
    reportes_directos = fields.Many2many('hr.employee', relation="red_reporte_rel", string='Reportes Directos')
    pares = fields.Many2many('hr.employee', relation="red_par_rel", string='Pares')
    clientes_internos = fields.Many2many('hr.employee', relation="red_cliente_interno_rel", string='Clientes Internos')
    
    state = fields.Selection([
        ('new', 'Nuevo'),
        ('pending', 'En espera de aprobación'),
        ('changes', 'Requiere cambios'),        
        ('approval', 'Aprobado'),
        ('rechazada', "Rechazado"),
    ], string='Status', tracking=True, required=True, copy=False, default='new', index=True)




