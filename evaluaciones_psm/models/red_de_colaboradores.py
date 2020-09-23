from odoo import models, fields, api, _


class RedDelColaborador(models.Model):
    _name = 'red.del.colaborador'
    _rec_name = 'colaborador'
    _description = "Red del Colaborador"

    red_de_evaluacion = fields.Many2one('red.de.evaluaciones', string='Red de evaluación')
    colaborador = fields.Many2one('hr.employee', string='Colaborador')
    colaboradores_a_evaluar = fields.Many2many('hr.employee', string='A evaluar')




