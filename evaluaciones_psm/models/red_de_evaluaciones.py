import datetime
from odoo import models, fields, api, _


class HrAppraisal(models.Model):
    _inherit = 'hr.appraisal'

    red_de_evaluacion = fields.Many2one('red.de.evaluaciones', string='Encuesta')


class RedDeEvaluaciones(models.Model):
    _name = 'red.de.evaluaciones'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'nombre'
    _description = "Red de Evaluaciones"

    nombre = fields.Char('Nombre')
    descripcion = fields.Char('Descripción')
    colaborador = fields.Many2many('red.del.colaborador', string="Colaborador")
    encuesta = fields.Many2one('survey.survey', string='Encuesta')
    fecha_limite = fields.Date(sting="Fecha limite")

    jefe_directo = fields.Boolean(string="Jefe Directo")
    companeros = fields.Boolean(string="Compañeros")
    reportes_directos = fields.Boolean(string="Reportes Directos")

    def generar_lista(self):

        colaboradores_ids = self.env['hr.employee'].search([])

        for id in colaboradores_ids:

            colaborador_model = self.env['red.del.colaborador'].create({'red_de_evaluacion': self.id,
                                                                        'colaborador': id.id
                                                                        })

            # Insertar Jefe Directo
            if self.jefe_directo:
                jefe_inmediato = colaborador_model.colaborador.parent_id
                if jefe_inmediato:
                    colaborador_model.write({'colaboradores_a_evaluar': [(4, jefe_inmediato.id)]})

            # Insertar Reportes Directos
            if self.reportes_directos:
                reportes_ids = self.env['hr.employee'].search([('parent_id', '=', id.id)])
                if reportes_ids:
                    for id in reportes_ids:
                        colaborador_model.write({'colaboradores_a_evaluar': [(4, id.id)]})

            # Insertar Compañeros
            if self.companeros:
                if id.department_id.id:
                    colegas_ids = self.env['hr.employee'].search([('department_id', '=', id.department_id.id)])
                    if colegas_ids:
                        for id in colegas_ids:
                            if id.id == colaborador_model.colaborador.id:
                                print("noes")
                            else:
                                colaborador_model.write({'colaboradores_a_evaluar': [(4, id.id)]})

            # Actualiza listado de colaboradores en Red de evaluaciones
            red_de_evaluaciones = self.env['red.de.evaluaciones'].search([('id', '=', self.id)])
            red_de_evaluaciones.write({'colaborador': [(4, colaborador_model.id)]})

    def limpiar_lista(self):
        self.env["red.del.colaborador"].search([('red_de_evaluacion', '=', self.id)]).unlink()

    # def _get_employees_to_appraise(self, months):
    #     days = int(self.env['ir.config_parameter'].sudo().get_param('hr_appraisal.appraisal_create_in_advance_days', 8))
    #     current_date = datetime.date.today()
    #     return self.search([
    #         ('appraisal_date', '<=', current_date - relativedelta(months=months, days=-days)),
    #     ])

    def generar_encuestas(self):

        colaboradores = self.colaborador

        if colaboradores:
            for id in colaboradores:

                colaborador_model = self.env['red.del.colaborador'].search([('id', '=', id.id)])

                if colaborador_model:

                    company_id = colaborador_model.colaborador.company_id.id
                    employee_id = colaborador_model.colaborador.id
                    date_close = self.fecha_limite
                    manager_ids = colaborador_model.colaborador.parent_id.id
                    manager_body_html = colaborador_model.colaborador.company_id.appraisal_by_manager_body_html
                    colleagues_ids = [(4, colleagues.id) for colleagues in colaborador_model.colaboradores_a_evaluar]
                    colleagues_body_html = colaborador_model.colaborador.company_id.appraisal_by_colleagues_body_html

                    if colleagues_ids:
                        if manager_ids:
                            manager_appraisal_boolean = True
                        else:
                            manager_appraisal_boolean = False
                            manager_ids = 0
                            manager_body_html = ''

                        if colleagues_ids:
                            colleagues_appraisal_boolean = True
                        else:
                            colleagues_appraisal_boolean = False
                            colleagues_ids = 0
                            colleagues_body_html = ''

                        manager_appraisal = manager_appraisal_boolean
                        colleagues_appraisal = colleagues_appraisal_boolean

                        appraisal_values = [{
                                'red_de_evaluacion': self.id,
                                'company_id': company_id,
                                'employee_id': employee_id,
                                'date_close': date_close,
                                'manager_appraisal': False,
                                'manager_ids': [],
                                'manager_body_html': '',
                                'colleagues_appraisal': colleagues_appraisal,
                                'colleagues_ids': colleagues_ids,
                                'colleagues_body_html': colleagues_body_html,
                                'employee_appraisal': False,
                                'collaborators_appraisal': False,
                            }]

                        appraisals = self.env['hr.appraisal'].create(appraisal_values)

        # body = colaboradores.company_id.appraisal_by_manager_body_html

        # current_date = datetime.date.today()
        # months = int(self.env['ir.config_parameter'].sudo().get_param('hr_appraisal.appraisal_max_period'))
        # # Set periodic_appraisal_created for the next appraisal if the date is passed:
        # # Create perdiodic appraisal if appraisal date is in less than a week and the appraisal for this perdiod has not been created yet:
        # employees_to_appraise = self._get_employees_to_appraise(months)
        # appraisal_values = [{
        #     'company_id': colaboradores.company_id.id,
        #     'employee_id': colaboradores.id,
        #     'date_close': self.fecha_limite,
        #     'manager_appraisal': colaboradores.appraisal_by_manager,
        #     'manager_ids': [(4, manager.id) for manager in colaboradores.appraisal_manager_ids],
        #     'manager_body_html': colaboradores.company_id.appraisal_by_manager_body_html,
        #     'colleagues_appraisal': colaboradores.appraisal_by_colleagues,
        #     'colleagues_ids': [(4, colleagues.id) for colleagues in colaboradores.appraisal_colleagues_ids],
        #     'colleagues_body_html': colaboradores.company_id.appraisal_by_colleagues_body_html,
        #     'employee_appraisal': colaboradores.appraisal_self,
        #     'employee_body_html': colaboradores.company_id.appraisal_by_employee_body_html,
        #     'collaborators_appraisal': colaboradores.appraisal_by_collaborators,
        #     'collaborators_ids': [(4, subordinates.id) for subordinates in colaboradores.appraisal_collaborators_ids],
        #     'collaborators_body_html': colaboradores.company_id.appraisal_by_collaborators_body_html,
        # } for colaboradores in employees_to_appraise]
        # appraisals = self.env['hr.appraisal'].create(appraisal_values)
