import datetime
from odoo import models, fields, api, _
from datetime import datetime, date
from datetime import timedelta


class SurveyUserInput(models.Model):
    _inherit = 'survey.user_input'

    evaluado = fields.Many2one('hr.employee', relation="survey_evaluado_rel", string='Evaluado')
    evaluador = fields.Many2one('hr.employee', relation="survey_evaluador_rel", string='Evaluador')


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

    def obten_total_colaboradores(self):
        total = self.env['red.del.colaborador'].search_count([('red_de_evaluacion', '=', self.id)])
        self.x_conteo_colaboradores = total

    def muestra_encuestas(self):
        return {
            'name': _('Encuestas'),
            'domain': [('survey_id', 'in', (self.jefe_directo.id, self.reportes_directos.id, self.cliente_interno.id, self.pares.id, self.autoevaluacion_lider.id, self.autoevaluacion.id))],
            'view_type': 'form',
            'res_model': 'survey.user_input',
            'view_id': False,
            'view_mode': 'tree,form',
            'context': {'group_by': 'state'},
            'type': 'ir.actions.act_window',
        }

    def obten_total_encuestas(self):
        total = self.env['survey.user_input'].search_count([('survey_id', 'in', (self.jefe_directo.id, self.reportes_directos.id, self.cliente_interno.id, self.pares.id, self.autoevaluacion_lider.id, self.autoevaluacion.id))])
        self.x_conteo_encuestas = total

    nombre = fields.Char('Nombre', required=True)
    descripcion = fields.Text('Descripción')
    colaborador = fields.Many2many('red.del.colaborador', string="Colaborador")
    fecha_inicio = fields.Date(sting="Fecha Inicio", required=True)
    fecha_limite = fields.Date(sting="Fecha limite", required=True)
    autoevaluacion = fields.Many2one('survey.survey', relation="survey_autoevaluacion_rel", string='Autoevaluación', required=True)
    autoevaluacion_lider = fields.Many2one('survey.survey', relation="survey_autoevaluacion_lider_rel", string='Autoevaluación Lider', required=True)
    jefe_directo = fields.Many2one('survey.survey', relation="survey_jefe_rel", string='Jefe', required=True)
    reportes_directos = fields.Many2one('survey.survey', relation="survey_reportes_rel", string='Reporte Directo', required=True)
    cliente_interno = fields.Many2one('survey.survey', relation="survey_cliente_rel", string='Cliente Interno', required=True)
    pares = fields.Many2one('survey.survey', relation="survey_par_rel", string='Par', required=True)
    evaluacion_body_html = fields.Html(string="Plantilla Correo Eléctronico", required=True)
    x_conteo_colaboradores = fields.Integer(string="Colaboradores", compute="obten_total_colaboradores")
    x_conteo_encuestas = fields.Integer(string="Encuestas", compute="obten_total_encuestas")

    def generar_lista(self):

        colaboradores_ids = self.env['hr.employee'].search([('active', '=', True), ('id', '!=', 1)])

        for id in colaboradores_ids:

            colaborador_model = self.env['red.del.colaborador'].create({'red_de_evaluacion': self.id, 'colaborador': id.id})

            # Inserta Jefe Directo
            jefe_inmediato = colaborador_model.colaborador.parent_id
            if jefe_inmediato:
                colaborador_model.write({'jefes': [(4, jefe_inmediato.id)]})

            # Inserta Reportes Directos
            reportes_ids = self.env['hr.employee'].search([('parent_id', '=', id.id)])
            if reportes_ids:
                for id in reportes_ids:
                    colaborador_model.write({'reportes_directos': [(4, id.id)]})

            # Actualiza listado de colaboradores en Red de evaluaciones
            red_de_evaluaciones = self.env['red.de.evaluaciones'].search([('id', '=', self.id)])
            red_de_evaluaciones.write({'colaborador': [(4, colaborador_model.id)]})

    def eliminar_colaboradores(self):
        self.env["red.del.colaborador"].search([('red_de_evaluacion', '=', self.id)]).unlink()

    def eliminar_encuestas(self):
        self.env["survey.user_input"].search([('survey_id', 'in', (self.jefe_directo.id, self.reportes_directos.id, self.cliente_interno.id, self.pares.id, self.autoevaluacion_lider.id, self.autoevaluacion.id))]).unlink()

    def generar_encuestas(self):

        # OBTENER LISTADO RED DE COLABORADORES
        colaboradores = self.colaborador

        if colaboradores:
            for colaborador in colaboradores:

                # OBTENER DATOS DEL COLABORADOR
                colaborador_data = self.env['red.del.colaborador'].search([('id', '=', colaborador.id)])

                if colaborador_data:
                    fecha_limite = self.fecha_limite
                    evaluado = colaborador_data.colaborador.id
                    html_buttons = ""

                    # JEFES
                    if colaborador_data.jefes:
                        for jefe in colaborador_data.jefes:
                            evaluador = jefe.id
                            # contacto = jefe.user_id.partner_id.id
                            # correo_electronico = jefe.user_id.partner_id.email
                            contacto = jefe.address_home_id.id
                            correo_electronico = jefe.address_home_id.email

                            survey_values = [{
                                'survey_id': self.jefe_directo.id,
                                'input_type': 'manually',
                                'state': 'new',
                                'partner_id': contacto,
                                'email': correo_electronico,
                                'deadline': fecha_limite,
                                'evaluado': evaluado,
                                'evaluador': evaluador,
                            }]

                            # GENERA ENCUESTA
#                             survey_user_input = self.env['survey.user_input'].create(survey_values)

                            answers = self._prepare_answers(contacto, correo_electronico)
                            for answer in answers:
                                self._send_mail(answer)

                    # REPORTES DIRECTOS
                    if colaborador_data.reportes_directos:
                        for reporte_directo in colaborador_data.reportes_directos:
                            evaluador = reporte_directo.id
                            # contacto = jefe.user_id.partner_id.id
                            # correo_electronico = jefe.user_id.partner_id.email
                            contacto = reporte_directo.address_home_id.id
                            correo_electronico = reporte_directo.address_home_id.email

                            survey_values = [{
                                'survey_id': self.reportes_directos.id,
                                'input_type': 'manually',
                                'state': 'new',
                                # 'test_entry': 'false',
                                'partner_id': contacto,
                                'email': correo_electronico,
                                'deadline': fecha_limite,
                                'evaluado': evaluado,
                                'evaluador': evaluador,
                            }]
                            
                            answers = self._prepare_answers(contacto, correo_electronico)
                            for answer in answers:
                                self._send_mail(answer)

                            # GENERA ENCUESTA
#                             survey_user_input = self.env['survey.user_input'].create(survey_values)

                        # AUTOEVALUACIÓN
                        evaluador = evaluado
                        # contacto = jefe.user_id.partner_id.id
                        # correo_electronico = jefe.user_id.partner_id.email
                        contacto = colaborador_data.colaborador.address_home_id.id
                        correo_electronico = colaborador_data.colaborador.address_home_id.email
                        survey_values = [{
                            'survey_id': self.autoevaluacion_lider.id,
                            'input_type': 'manually',
                            'state': 'new',
                            # 'test_entry': 'false',
                            'partner_id': contacto,
                            'email': correo_electronico,
                            'deadline': fecha_limite,
                            'evaluado': evaluado,
                            'evaluador': evaluado,
                        }]
                        
                        answers = self._prepare_answers(contacto, correo_electronico)
                        for answer in answers:
                            self._send_mail(answer)

                        # GENERA ENCUESTA
                        # survey_user_input = self.env['survey.user_input'].create(survey_values)

                    else:

                        # AUTOEVALUACIÓN
                        evaluador = evaluado
                        # contacto = jefe.user_id.partner_id.id
                        # correo_electronico = jefe.user_id.partner_id.email
                        contacto = colaborador_data.colaborador.address_home_id.id
                        correo_electronico = colaborador_data.colaborador.address_home_id.email
                        survey_values = [{
                            'survey_id': self.autoevaluacion.id,
                            'input_type': 'manually',
                            'state': 'new',
                            # 'test_entry': 'false',
                            'partner_id': contacto,
                            'email': correo_electronico,
                            'deadline': fecha_limite,
                            'evaluado': evaluado,
                            'evaluador': evaluado,
                        }]
                        
                        answers = self._prepare_answers(contacto, correo_electronico)
                        for answer in answers:
                            self._send_mail(answer)

                        # GENERA ENCUESTA
                        # survey_user_input = self.env['survey.user_input'].create(survey_values)

                    # CLIENTE INTERNO
                    if colaborador_data.clientes_internos:
                        for cliente_interno in colaborador_data.clientes_internos:
                            evaluador = cliente_interno.id
                            # contacto = jefe.user_id.partner_id.id
                            # correo_electronico = jefe.user_id.partner_id.email
                            contacto = cliente_interno.address_home_id.id
                            correo_electronico = cliente_interno.address_home_id.email

                            survey_values = [{
                                'survey_id': self.cliente_interno.id,
                                'input_type': 'manually',
                                'state': 'new',
                                # 'test_entry': 'alse',
                                'partner_id': contacto,
                                'email': correo_electronico,
                                'deadline': fecha_limite,
                                'evaluado': evaluado,
                                'evaluador': evaluador,
                            }]
                            
                            answers = self._prepare_answers(contacto, correo_electronico)
                            for answer in answers:
                                self._send_mail(answer)

                            # GENERA ENCUESTA
                            # survey_user_input = self.env['survey.user_input'].create(survey_values)

                    # PARES
                    if colaborador_data.pares:
                        for pares in colaborador_data.pares:
                            evaluador = pares.id
                            # contacto = jefe.user_id.partner_id.id
                            # correo_electronico = jefe.user_id.partner_id.email
                            contacto = pares.address_home_id.id
                            correo_electronico = pares.address_home_id.email

                            survey_values = [{
                                'survey_id': self.cliente_interno.id,
                                'input_type': 'manually',
                                'state': 'new',
                                # 'test_entry': 'false',
                                'partner_id': contacto,
                                'email': correo_electronico,
                                'deadline': fecha_limite,
                                'evaluado': evaluado,
                                'evaluador': evaluador,
                            }]
                            
                            answers = self._prepare_answers(contacto, correo_electronico)
                            for answer in answers:
                                self._send_mail(answer)

                            # GENERA ENCUESTA
                            # survey_user_input = self.env['survey.user_input'].create(survey_values)

    # def generar_actividad(self):
    #     self.env['mail.activity'].create({
    #         'res_id': 1,
    #         'res_model_id': self.env['ir.model']._get('hr.employee').id,
    #         'summary': 'Evaluación',
    #         'note': 'Nota Evaluación',
    #         'activity_type_id': 4,
    #         'user_id': 2,
    #         'date_deadline': date.today(),
    #     })

    def enviar_encuestas(self):
        colaboradores = self.env['red.del.colaborador'].search([('red_de_evaluacion', '=', self.id)])
        if colaboradores:
            for colaborador in colaboradores:

                encuesta_jefe_directo = self.jefe_directo.id
                encuesta_reportes_directos = self.reportes_directos.id
                encuesta_cliente_interno = self.cliente_interno.id
                encuesta_pares = self.pares.id
                encuesta_autoevaluacion_lider = self.autoevaluacion_lider.id
                encuesta_autoevaluacion = self.autoevaluacion.id
                encuestas = self.env["survey.user_input"].search([('evaluador', '=', colaborador.colaborador.id),
                                                                  ('survey_id', 'in', (encuesta_jefe_directo,
                                                                                       encuesta_reportes_directos,
                                                                                       encuesta_cliente_interno,
                                                                                       encuesta_pares,
                                                                                       encuesta_autoevaluacion_lider,
                                                                                       encuesta_autoevaluacion))])

                if encuestas:
                    html_buttons = ""
                    boton_plantilla = "<div style=' margin:16px 0px 16px 0px'>" \
                                      "<a href='[link]' style='color:#fff; " \
                                      "background-color:#875A7B; " \
                                      "padding:8px 16px 8px 16px; " \
                                      "text-decoration:none; " \
                                      "border-radius:5px; " \
                                      "font-size:13px'>[evaluado]</a></div>"

                    # URL ACTUAL
                    base_url = self.env['ir.config_parameter'].get_param('web.base.url')
                    base_url = base_url + "/survey/start/"

                    for encuesta in encuestas:
                        # LINKS
                        boton = ""
                        texto_boton = ""
                        link = base_url + encuesta.survey_id.access_token + "?answer_token=" + encuesta.token

                        if encuesta.evaluado.id == encuesta.evaluador.id:
                            texto_boton = "Autoevaluación "
                        else:
                            texto_boton = "Evaluación de "

                        nombre_evaluado = encuesta.evaluado.name
                        boton = boton_plantilla + boton
                        boton = boton.replace("[link]", link)
                        boton = boton.replace("[evaluado]", texto_boton + nombre_evaluado)

                        html_buttons = html_buttons + boton

                        # GENERAR ACTIVIDADES
                        self.env['mail.activity'].create({
                            'res_id': colaborador.colaborador.id,
                            'res_model_id': self.env['ir.model']._get('hr.employee').id,
                            'summary': colaboradores.red_de_evaluacion.nombre,
                            'note': 'El periodo limite para la evaluación es el ' + encuesta.deadline.strftime('%d/%m/%Y') + ' ' + boton,
                            'activity_type_id': 4,
                            'user_id': colaborador.colaborador.user_id.id,
                            'date_deadline': date.today(),
                        })

                # PLANTILLA DE CORREO ELECTRONICO
                subject = colaboradores.red_de_evaluacion.nombre
                body = self.evaluacion_body_html.replace("[Botones]", html_buttons)
                body = body.replace("[Evaluador]", colaborador.colaborador.name).replace("[FechaLimite]", self.fecha_limite.strftime('%d/%m/%Y'))
                author_id = self.create_uid.id
                email_from = self.create_uid.email
                mail_values = {
                    'email_from': colaborador.colaborador.work_email,
                    'author_id': author_id,
                    'model': None,
                    'res_id': None,
                    'subject': subject,
                    'body_html': body,
                    'auto_delete': True,
                    'recipient_ids': [(4, colaborador.colaborador.user_id.partner_id.id)]
                }

                # ENVIA CORREO
                self.env['mail.mail'].sudo().create(mail_values).send()

    #-------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------
    #-------------------------------------------------------------------------------------

    def _prepare_answers(self, partners, emails):
        answers = self.env['survey.user_input']
        answers |= self._create_answer(partner=partners, check_attempts=False, **self._get_answers_values())
        return answers
    
    def _get_answers_values(self):
        return {
            'input_type': 'link',
            'deadline': self.fecha_limite,
        }
    
    def _create_answer(self, user=False, partner=False, email=False, test_entry=False, check_attempts=True, **additional_vals):
        """ Main entry point to get a token back or create a new one. This method
        does check for current user access in order to explicitely validate
        security.
    
          :param user: target user asking for a token; it might be void or a
                       public user in which case an email is welcomed;
          :param email: email of the person asking the token is no user exists;
        """
        self.check_access_rights('read')
        self.check_access_rule('read')
    
        answers = self.env['survey.user_input']
#         for survey in self:
        user = self.colaborador.colaborador.user_id
    
        invite_token = additional_vals.pop('invite_token', False)
        
        answer_vals = {
            'survey_id': 31,
            'test_entry': test_entry,
                # 'question_ids': [(6, 0, survey._prepare_answer_questions().ids)]
            }
#             if user and not user._is_public():
#             if user:
#                 answer_vals['partner_id'] = user.partner_id.id
#                 answer_vals['email'] = user.email
#             elif partner:
#                 answer_vals['partner_id'] = partner.id
#                 answer_vals['email'] = partner.email
#             else:
#                 answer_vals['email'] = email
    
#             answer_vals['partner_id'] = '693'
        answer_vals.update(additional_vals)
    
        answer_vals['email'] = 'enrique.alfaro@psm.org.mx'
           
        if invite_token:  
            answer_vals['invite_token'] = invite_token
            answers += answers.create(answer_vals)
            
        return answers

    def create_invite(self):
        link = "<div style='font-size:13px; font-family:'Lucida Grande', Helvetica, Verdana, Arial, sans-serif; margin:0px; padding:0px'> " \
               "<p style='margin:0px; font-size:13px; font-family:'Lucida Grande', Helvetica, Verdana, Arial, sans-serif; padding:0px'>" \
               "Dear ${object.partner_id.name or 'participant'}<br><br> % if object.survey_id.certificate: You have been invited to take a new certification." \
               " % else: We are conducting a survey and your response would be appreciated. " \
               "% endif </p><div style='font-size:13px; font-family:'Lucida Grande', " \
               "Helvetica, Verdana, Arial, sans-serif; margin:16px 0px 16px 0px'>" \
               "<a href='${('%s?answer_token=%s' % (object.survey_id.public_url, object.token)) | safe}' " \
               "style='text-decoration:none; color:#fff; background-color:#875A7B; padding:8px 16px 8px 16px; border-radius:5px; font-size:13px;'>" \
               " % if object.survey_id.certificate: Start Certification " \
               " % else: Start Survey % endif </a>" \
               "</div> % if object.deadline: Please answer the survey for ${format_date(object.deadline)}.<br><br> " \
               "% endif Thank you for your participation. <p style='margin:0px; font-size:13px; font-family:'Lucida Grande', Helvetica, Verdana, Arial, sans-serif'></p>" \
               "</div>"
    
        survey_values_invite = [{
            'subject': 'Participate to ${object.survey_id.title} survey',
            'body': link,
            'template_id': 26,
            'email_from': '"Administrator" <admin@example.com>',
            'author_id': 3,
            'existing_mode': 'resend',
            'survey_id': 1,
            # 'deadline': '',
        }]
    
        survey_invite = self.env['survey.invite'].create(survey_values_invite)
                
        # def _send_mail(self, answer):
        # """ Create mail specific for recipient containing notably its access token """
#         subject = self.env['mail.template']._render_template(self.subject, 'survey.user_input', answer.id, post_process=True)
#         body = self.env['mail.template']._render_template(self.body, 'survey.user_input', answer.id, post_process=True)
        # post the message
#         mail_values = {
#             'email_from': self.email_from,
#             'author_id': self.author_id.id,
#             'model': None,
#             'res_id': None,
#             'subject': 'subject',
#             'body_html': 'body',
# #             'attachment_ids': [(4, att.id) for att in self.attachment_ids],
#             'auto_delete': True,
#         }
#         if answer.partner_id:
#             mail_values['recipient_ids'] = [(4, answer.partner_id.id)]
#         else:
#             mail_values['email_to'] = answer.email
    
        # optional support of notif_layout in context
        # notif_layout = self.env.context.get('notif_layout', self.env.context.get('custom_layout'))
        # if notif_layout:
            # try:
            #     template = self.env.ref(notif_layout, raise_if_not_found=True)
            # except ValueError:
            #     _logger.warning('QWeb template %s not found when sending survey mails. Sending without layouting.' % (notif_layout))
            # else:
            #     template_ctx = {
            #         'message': self.env['mail.message'].sudo().new(dict(body=mail_values['body_html'], record_name=self.survey_id.title)),
            #         'model_description': self.env['ir.model']._get('survey.survey').display_name,
            #         'company': self.env.company,
            #     }
            #     body = template.render(template_ctx, engine='ir.qweb', minimal_qcontext=True)
            #     mail_values['body_html'] = self.env['mail.thread']._replace_local_links(body)
    
#         return self.env['mail.mail'].sudo().create(mail_values)