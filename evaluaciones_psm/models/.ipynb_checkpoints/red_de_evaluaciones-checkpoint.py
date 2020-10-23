import datetime
from odoo import models, fields, api, _
from datetime import datetime, date
from datetime import timedelta
import uuid


class SurveyUserInput(models.Model):
    """ Metadatos heredados para poder identificar al evaluado y evaluador de la encuesta """
    _inherit = 'survey.user_input'

    evaluado = fields.Many2one('hr.employee', relation="survey_evaluado_rel", string='Evaluado')
    evaluador = fields.Many2one('hr.employee', relation="survey_evaluador_rel", string='Evaluador')


class RedDeEvaluaciones(models.Model):
    """ Metadatos para generar una nueva red de evaluación """
    _name = 'red.de.evaluaciones'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'nombre'
    _description = "Mapeo de Evaluaciones"

    # -----------------------------------------------------------------------------------------------
    # Boton inteligente colaborador
    # -----------------------------------------------------------------------------------------------
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

    # -----------------------------------------------------------------------------------------------
    # Boton inteligente de encuesta
    # -----------------------------------------------------------------------------------------------
    def muestra_encuestas(self):
        return {
            'name': _('Encuestas'),
            'domain': [('survey_id', 'in', (
            self.jefe_directo.id, self.reportes_directos.id, self.cliente_interno.id, self.pares.id,
            self.autoevaluacion_lider.id, self.autoevaluacion.id))],
            'view_type': 'form',
            'res_model': 'survey.user_input',
            'view_id': False,
            'view_mode': 'tree,form',
            'context': {'group_by': ['state', 'evaluador']},
            'type': 'ir.actions.act_window',
        }

    def obten_total_encuestas(self):
        total = self.env['survey.user_input'].search_count([('survey_id', 'in', (
        self.jefe_directo.id, self.reportes_directos.id, self.cliente_interno.id, self.pares.id,
        self.autoevaluacion_lider.id, self.autoevaluacion.id))])
        self.x_conteo_encuestas = total

    # -----------------------------------------------------------------------------------------------
    # Boton de finalización de evaluación
    # -----------------------------------------------------------------------------------------------
    def finalizar_evaluacion(self):
        for rec in self:
            rec.state = 'done'
            rec.fecha_fin = datetime.now()
        return self._mensaje('', 'Evaluación Finalizada')

    # -----------------------------------------------------------------------------------------------
    # Campos
    # -----------------------------------------------------------------------------------------------
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
    evaluacion_body_html = fields.Html(string="Plantilla Correo Eléctronico", required=True, default='Su plantilla debe contener las siguientes etiquetas: [Evaluador] [Botones] [FechaLimite]')
    fecha_envio = fields.Datetime(sting="Fecha de Envío")
    fecha_fin = fields.Datetime(sting="Fecha de Finalización")

    # Campos usados en los botones inteligentes
    x_conteo_colaboradores = fields.Integer(string="Colaboradores", compute="obten_total_colaboradores")
    x_conteo_encuestas = fields.Integer(string="Encuestas", compute="obten_total_encuestas")

    # Campo para el estado de la evaluación
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('send', 'Enviada'),
        ('done', 'Finalizada'),
    ], string='Estado', tracking=True, default='draft', index=True, readonly=True)

    # -----------------------------------------------------------------------------------------------
    # Acciones Red de colaboradores
    # -----------------------------------------------------------------------------------------------
    def genera_lista_de_colaboradores(self):
        """ Acciones de este metodo:
        1.- Obtiene listado de todos los empleados activos
        2.- Inicia ciclo for para extraer los datos de cada empleado
            - Crea nuevo registro del empleado en la red del colaborador
            - Obtiene a su jefe directo y lo inserta
            - Obtiene a sus reportes directos y los inserta
            - Actualiza la red de evaluación con el colaborador creado
            - Envia mensaje a la vista
        """

        titulo_mensaje = ""
        lista_empleados = self.env['hr.employee'].search([('active', '=', True), ('id', '!=', 1)])
        if lista_empleados:
            for id_empleado in lista_empleados:
                colaborador_creado = self.env['red.del.colaborador'].create({'red_de_evaluacion': self.id, 'colaborador': id_empleado.id})

                id_jefe = colaborador_creado.colaborador.parent_id.id
                if id_jefe:
                    colaborador_creado.write({'jefes': [(4, id_jefe)]})

                lista_reportes_directos = self.env['hr.employee'].search([('parent_id', '=', id_empleado.id)])
                if lista_reportes_directos:
                    for reporte_directo in lista_reportes_directos:
                        colaborador_creado.write({'reportes_directos': [(4, reporte_directo.id)]})

                red_de_evaluaciones = self.env['red.de.evaluaciones'].search([('id', '=', self.id)])
                red_de_evaluaciones.write({'colaborador': [(4, colaborador_creado.id)]})

            mensaje = "Red del colaborador creado satisfactoriamente."
        else:
            titulo_mensaje = 'Restricción'
            mensaje = 'No hay empleados activos.'

        return self._mensaje(titulo_mensaje, mensaje)

    # -----------------------------------------------------------------------------------------------
    # Acciones Generar Encuestas
    # -----------------------------------------------------------------------------------------------
    def genera_encuestas(self):
        """ Acciones de este metodo:
        1.- Obtiene listado de la red de colaboradores
        2.- Inicia ciclo for para extraer los datos de cada colaborador
            - Crea registro del colaborador en la encuesta (Modelo user_input)
            - Crea invitaciones para los evaluadores (Modelo survey_invite)
        """
        titulo_mensaje = ""
        lista_colaboradores = self.colaborador
        if lista_colaboradores:
            for colaborador in lista_colaboradores:
                datos_colaborador = self.env['red.del.colaborador'].search([('id', '=', colaborador.id)])
                if datos_colaborador:
                    id_evaluado = datos_colaborador.colaborador.id

                    # Evaluaciones
                    if datos_colaborador.jefes:
                        self._obtiene_datos_evaluador(datos_colaborador.jefes, id_evaluado, self.jefe_directo.id, self.fecha_limite)
                    if datos_colaborador.reportes_directos:
                        self._obtiene_datos_evaluador(datos_colaborador.reportes_directos, id_evaluado, self.reportes_directos.id, self.fecha_limite)
                    if datos_colaborador.clientes_internos:
                        self._obtiene_datos_evaluador(datos_colaborador.clientes_internos, id_evaluado, self.cliente_interno.id, self.fecha_limite)
                    if datos_colaborador.pares:
                        self._obtiene_datos_evaluador(datos_colaborador.pares, id_evaluado, self.pares.id, self.fecha_limite)

                    # Autoevaluaciones
                    if datos_colaborador.reportes_directos:
                        encuesta_autoevaluacion = self.autoevaluacion_lider.id
                    else:
                        encuesta_autoevaluacion = self.autoevaluacion.id

                    self._genera_autoevaluacion(datos_colaborador.colaborador, encuesta_autoevaluacion, self.fecha_limite)

            mensaje = "Encuestas de los colaboradores generadas satisfactoriamente"

        else:
            titulo_mensaje = 'Restricción'
            mensaje = 'No hay colaboradores en la red.'

        return self._mensaje(titulo_mensaje, mensaje)

    def _genera_autoevaluacion(self, evaluado, id_encuesta, fecha_limite):

        id_evaluado = evaluado.id
        id_contacto = evaluado.user_id.partner_id.id
        correo_electronico = evaluado.user_id.partner_id.email

        self._crea_registro_encuesta(id_encuesta,
                                     id_contacto,
                                     correo_electronico,
                                     fecha_limite,
                                     id_evaluado,
                                     id_evaluado)

    def _obtiene_datos_evaluador(self, evaluadores, id_evaluado, id_encuesta, fecha_limite):

        for evaluador in evaluadores:

            id_contacto = evaluador.user_id.partner_id.id
            correo_electronico = evaluador.user_id.partner_id.email

            self._crea_registro_encuesta(id_encuesta,
                                         id_contacto,
                                         correo_electronico,
                                         fecha_limite,
                                         id_evaluado,
                                         evaluador.id)

    def _crea_registro_encuesta(self, id_encuesta, id_contacto, correo_electronico, fecha_limite, id_evaluado, id_evaluador):

        vals = [{
            'survey_id': id_encuesta,
            'input_type': 'link',
            'state': 'new',
            'partner_id': id_contacto,
            'email': correo_electronico,
            'deadline': fecha_limite,
            'evaluado': id_evaluado,
            'evaluador': id_evaluador,
            'token': uuid.uuid4()
        }]
        survey_user_input = self.env['survey.user_input'].create(vals)

        preguntas = self.env['survey.question'].search([('survey_id', '=', id_encuesta)])

        if preguntas:
            for pregunta in preguntas:
                self.env.cr.execute(
                    """INSERT INTO survey_question_survey_user_input_rel (survey_user_input_id, survey_question_id) VALUES (%s, %s);""",
                    (survey_user_input.id, pregunta.id))

    # -----------------------------------------------------------------------------------------------
    # Acciones Enviar Encuestas
    # -----------------------------------------------------------------------------------------------
    def envia_encuestas(self):
        """Acciones de este metodo:
        1.- Obtiene listado de la red de colaboradores
        2.- Inicia ciclo for para extraer los datos de cada colaborador
            - Obtiene encuestas del evaluador
            - Inicia ciclo for para extraer datos de la encuesta del usuario
                - Obtiene la URL actual
                - Crea los botones por encuesta
                - Genera actividades en el modulo de empleados
                - Crea invitaciones (Modelo survey_invite)
        3.- Envia un correo con todas las encuestas que tiene que evaluar el colaborador
        """
        titulo_mensaje = ""
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
                                      "<a href='[link]' style='color:#1800bd; " \
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
                            'note': 'La fecha limite de la evaluación es el ' + encuesta.deadline.strftime('%d/%m/%Y') + ' ' + boton,
                            'activity_type_id': 4,
                            'user_id': colaborador.colaborador.user_id.id,
                            'date_deadline': date.today(),
                        })

                        # ENVIAR MENSAJE
                        #
                        # empleado = self.env['hr.employee'].search([('id', '=', colaborador.colaborador.id)])
                        # empleado.message_post(
                        #     partner_ids=[colaborador.colaborador.user_id.id],
                        #     subject= 'Evaluación 2020',
                        #     body=boton,
                        #     subtype_id=self.env.ref('mail.mt_comment').id,
                        #     email_layout_xmlid='mail.mail_notification_light',
                        # )

                        # CREA INVITACIÓN
                        plantilla = self.env['mail.template'].search([('name', '=', 'Survey: Invite')])

                        if plantilla:
                            survey_values_invite = [{
                                'subject': plantilla.subject,
                                'body': plantilla.body_html,
                                'template_id': plantilla.id,
                                'email_from': self.create_uid.partner_id.email,
                                'author_id': self.create_uid.partner_id.id,
                                'existing_mode': 'resend',
                                'survey_id': encuesta.survey_id.id,
                                'deadline': self.fecha_limite,
                            }]
                            invite = self.env['survey.invite'].create(survey_values_invite)
                            self.env.cr.execute("""
                                        INSERT INTO survey_invite_partner_ids (invite_id, partner_id) VALUES (%s, %s);
                                        """, (invite.id, colaborador.colaborador.user_id.partner_id.id))

                # PLANTILLA DE CORREO ELECTRONICO
                subject = colaboradores.red_de_evaluacion.nombre
                body = self.evaluacion_body_html.replace("[Botones]", html_buttons)
                body = body.replace("[Evaluador]", colaborador.colaborador.name).replace("[FechaLimite]",
                                                                                         self.fecha_limite.strftime(
                                                                                             '%d/%m/%Y'))
                author_id = self.create_uid.partner_id.id
                email_from = self.create_uid.partner_id.email
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

            red_actual = self.env['red.de.evaluaciones'].search([('id', '=', self.id)])
            red_actual.write({'fecha_envio': datetime.now(), 'state': 'send'})
            mensaje = "Encuestas enviadas satisfactoriamente"
        else:
            titulo_mensaje = "Restricción"
            mensaje = "No hay encuestas para enviar"

        return self._mensaje(titulo_mensaje, mensaje)

    # -----------------------------------------------------------------------------------------------
    # CRUD
    # -----------------------------------------------------------------------------------------------

    def _mensaje(self, titulo, mensaje):
        if titulo:
            return {
                'value': {},
                'warning': {'title': titulo,
                            'message': mensaje}
            }
        else:
            return {
                'effect': {
                    'fadeout': 'medium',
                    'message': mensaje,
                    'type': 'rainbow_man'
                }
            }






