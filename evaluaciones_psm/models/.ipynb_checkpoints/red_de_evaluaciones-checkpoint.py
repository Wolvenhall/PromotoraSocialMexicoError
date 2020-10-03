import datetime
from odoo import models, fields, api, _


class HrAppraisal(models.Model):
    _inherit = 'hr.appraisal'

    red_de_evaluacion = fields.Many2one('red.de.evaluaciones', string='Red de evaluación')


class RedDeEvaluaciones(models.Model):
    _name = 'red.de.evaluaciones'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'nombre'
    _description = "Red de Evaluaciones"   
    
    def muestra_colaboradores(self):
        return {
            'name': _('Colaboradores'),
            'domain': [('red_de_evaluacion', '=', self.id)],
            'view_type': 'form',
            'res_model': 'red.del.colaborador',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
    
    def muestra_evaluaciones(self):
        return {
            'name': _('Evaluaciones'),
            'domain': [('red_de_evaluacion', '=', self.id)],
            'view_type': 'form',
            'res_model': 'hr.appraisal',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }
    
    def obten_total_colaboradores(self):
        total = self.env['red.del.colaborador'].search_count([('red_de_evaluacion', '=', self.id)])
        self.x_conteo_colaboradores = total
        
    def obten_total_evaluaciones(self):
        total = self.env['hr.appraisal'].search_count([('red_de_evaluacion', '=', self.id)])
        self.x_conteo_evaluaciones = total

    nombre = fields.Char('Nombre')
    descripcion = fields.Char('Descripción')
    colaborador = fields.Many2many('red.del.colaborador', string="Colaborador")
    fecha_inicio = fields.Date(sting="Fecha Inicio")
    fecha_limite = fields.Date(sting="Fecha limite")

    jefe_directo = fields.Boolean(string="Jefe Directo")
    companeros = fields.Boolean(string="Compañeros")
    reportes_directos = fields.Boolean(string="Reportes Directos")
    
    autoevaluacion = fields.Many2one('survey.survey', relation="survey_ae_rel", string='AE')
    autoevaluacion_liderazgo = fields.Many2one('survey.survey', relation="survey_ae_liderazgo_rel", string='AE Liderazgo')
    general = fields.Many2one('survey.survey', relation="survey_general_rel", string='Evaluación')
    liderazgo = fields.Many2one('survey.survey', relation="survey_liderazgo_rel", string='Liderazgo')
    
    x_conteo_colaboradores = fields.Integer(string="Red Evaluación", compute="obten_total_colaboradores")
    x_conteo_evaluaciones = fields.Integer(string="Evaluaciones", compute="obten_total_evaluaciones")

    def generar_lista(self):

        colaboradores_ids = self.env['hr.employee'].search([('active', '=', True), ('id', '!=', 1)])

        for id in colaboradores_ids:

            colaborador_model = self.env['red.del.colaborador'].create({'red_de_evaluacion': self.id,
                                                                        'colaborador': id.id
                                                                        })

            # Insertar Jefe Directo
            if self.jefe_directo:
                jefe_inmediato = colaborador_model.colaborador.parent_id
                if jefe_inmediato:
                    colaborador_model.write({'jefes': [(4, jefe_inmediato.id)]})

            # Insertar Reportes Directos
            if self.reportes_directos:
                reportes_ids = self.env['hr.employee'].search([('parent_id', '=', id.id)])
                if reportes_ids:
                    for id in reportes_ids:
                        colaborador_model.write({'reportes_directos': [(4, id.id)]})

            # Insertar Compañeros
#             if self.companeros:
#                 if id.department_id.id:
#                     colegas_ids = self.env['hr.employee'].search([('department_id', '=', id.department_id.id), 
#                                                                   ('id', '!=', colaborador_model.colaborador.parent_id.id)])
#                     if colegas_ids:
#                         for id in colegas_ids:
#                             if id.id == colaborador_model.colaborador.id:
#                                 print("noes")
#                             else:
#                                 colaborador_model.write({'pares': [(4, id.id)]})
                                
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
                
                # OBTENER COLABORADOR
                colaborador_model = self.env['red.del.colaborador'].search([('id', '=', id.id)])

                if colaborador_model:
                    
                    # VARIABLES
                    company_id = colaborador_model.colaborador.company_id.id
                    employee_id = colaborador_model.colaborador.id
                    date_close = self.fecha_limite
                    manager_ids = 0
                    colleagues_ids = 0
                    collaborators_ids = 0
                    manager_body_html = 0
                    colleagues_body_html = 0
                    collaborators_body_html = 0
                    
                    # EMPLEADO
                    employee_body_html = colaborador_model.colaborador.company_id.appraisal_by_employee_body_html
                                        
                    # JEFES                
                    if colaborador_model.jefes:
                        manager_ids = [(4, managers.id) for managers in colaborador_model.jefes]
                        manager_body_html = colaborador_model.colaborador.company_id.appraisal_by_manager_body_html
                    
                    # REPORTES DIRECTOS
                    if colaborador_model.reportes_directos:
                        colleagues_ids = [(4, colleagues.id) for colleagues in colaborador_model.reportes_directos]
                        colleagues_body_html = colaborador_model.colaborador.company_id.appraisal_by_colleagues_body_html
                    
                    # PARES
                    if colaborador_model.pares:
                        collaborators_ids = [(4, collaborators.id) for collaborators in colaborador_model.pares]
                        collaborators_body_html = colaborador_model.colaborador.company_id.appraisal_by_collaborators_body_html
                        
                    # CLIENTES INTERNOS
                    if colaborador_model.clientes_internos:
                        clientes_ids = [(4, clientes.id) for clientes in colaborador_model.clientes_internos]         
                        collaborators_ids = collaborators_ids + clientes_ids
                                            
                    # URL ACTUAL                    
                    base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                    base_url = base_url + "/survey/start/"
                    
                    # ENCUESTAS      
                    autoevaluacion = self.env['survey.survey'].search([('id', '=', self.autoevaluacion.id)])
                    autoevaluacion_liderazgo = self.env['survey.survey'].search([('id', '=', self.autoevaluacion_liderazgo.id)])
                    evaluacion = self.env['survey.survey'].search([('id', '=', self.general.id)])
                    liderazgo = self.env['survey.survey'].search([('id', '=', self.liderazgo.id)])                    
                    
                    # LINKS
                    link_autoevaluacion = base_url + autoevaluacion.access_token
                    link_autoevaluacion_liderazgo = base_url + autoevaluacion_liderazgo.access_token
                    link_evaluacion = base_url + evaluacion.access_token
                    link_liderazgo = base_url + liderazgo.access_token
                    
                    # BOLEANOS
                    manager_appraisal_boolean = False        
                    colleague_appraisal_boolean = False  
                    collaborator_appraisal_boolean = False  
                    
                    if manager_ids:
                        manager_appraisal_boolean = True                        
                        manager_body_html = manager_body_html.replace("[link]", link_evaluacion)
                    else:
                        manager_ids = []        
                        manager_body_html = ''
                        
                    if colleagues_ids:
                        colleague_appraisal_boolean = True                        
                        colleagues_body_html = colleagues_body_html.replace("[link]", link_liderazgo)
                        employee_body_html = employee_body_html.replace("[link]", link_autoevaluacion_liderazgo)                        
                    else:
                        colleagues_ids = []   
                        colleagues_body_html = ''
                        employee_body_html = employee_body_html.replace("[link]", link_autoevaluacion)   
                        
                    if collaborators_ids:
                        collaborator_appraisal_boolean = True                        
                        collaborators_body_html = collaborators_body_html.replace("[link]", link_evaluacion)
                    else:
                        collaborators_ids = []
                        collaborators_body_html = ''
                                                                    
                                            
                    appraisal_values = [{
                                'red_de_evaluacion': self.id,
                                'company_id': company_id,
                                'employee_id': employee_id,
                                'date_close': date_close,
                            
                                'employee_appraisal': True,
                                'employee_body_html': employee_body_html,
                                                                                        
                                'manager_appraisal': manager_appraisal_boolean,
                                'manager_ids': manager_ids,
                                'manager_body_html': manager_body_html,
                                
                                'colleagues_appraisal': collaborator_appraisal_boolean,
                                'colleagues_ids': collaborators_ids,
                                'colleagues_body_html': collaborators_body_html,
                                                            
                                'collaborators_appraisal': colleague_appraisal_boolean,
                                'collaborators_ids': colleagues_ids,
                                'collaborators_body_html': colleagues_body_html,         
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
