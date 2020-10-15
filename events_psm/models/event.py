import requests
import base64
from odoo import models, api, _, fields
from datetime import datetime
from odoo.http import request
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import timedelta
from odoo import modules


class Event(models.Model):
    _inherit = "event.event"

    x_solicitud_de_evento = fields.Many2one('approval.request', string="Solicitud")
    x_solicitud_enviada_en = fields.Selection(selection=[('tiempo', 'Tiempo'), ('destiempo', 'Destiempo'), ],
                                              string=_('Solicitud enviada en '), )
    x_solicitante = fields.Char(string="Solicitante", related='x_solicitud_de_evento.request_owner_id.name')
    x_objetivo = fields.Text(string="Objetivo", related='x_solicitud_de_evento.x_objetivo')
    x_descripcion = fields.Text(string="Descripción", related='x_solicitud_de_evento.reason')
    x_host = fields.Many2one(string="Host", related='x_solicitud_de_evento.x_colaborador')
    x_departamento = fields.Char(string='Departamento', related='x_solicitud_de_evento.x_departamento')
    x_organizadores = fields.Many2many('res.partner', 'event_organizadores_rel', string="Organizadores")
    x_quien_paga_el_evento = fields.Selection(
        selection=[('Interno', 'Interno'), ('Externo', 'Externo'), ('Ambos', 'Ambos')],
        string=_('¿Quien paga el evento?'), )
    x_porcentaje_que_paga_psm = fields.Float(string="Porcentaje que paga PSM",
                                             related='x_solicitud_de_evento.x_porcentaje_que_paga_psm')
    x_audiencia = fields.Many2many('event.audiencia', string="Audiencia")

    x_area = fields.Many2many('event.area', string="Área")
    x_coordinador = fields.Many2one(string="Coordinador", related='x_solicitud_de_evento.x_cordinador')
    x_brigadista = fields.Many2one(string="Brigadista", related='x_solicitud_de_evento.x_brigadista')

    x_tipo_de_evento = fields.Selection(
        selection=[('Cerrado / Privado sólo para invitados', 'Cerrado / Privado sólo para invitados'),
                   ('Abierto para colaboradores', 'Abierto para colaboradores')], string=_('Tipo de evento'), )
    x_colaboradores_adicionales = fields.Integer(string="Colaboradores Adicionales")
    x_requiere_catering = fields.Selection(selection=[('si', 'Sí'), ('no', 'No'), ], string=_('¿Requiere catering?'), )
    x_budget_proyectado = fields.Float(string="Budget proyectado")

    x_hora_de_registro = fields.Datetime(string="Hora de registro")
    x_hora_de_salida = fields.Datetime(string="Hora de salida")
    x_duracion_del_evento = fields.Char(string='Duracion evento (hrs)')
    x_numero_de_asistentes = fields.Integer(string="Asistentes reales")

    x_distribucion = fields.Many2one('event.distribucion', string="Distribución")
    x_especificacion_de_distribucion = fields.Text(string="Especificación")

    x_servicio_de_ceremonias = fields.Selection(
        selection=[('Durante todo el evento', 'Durante todo el evento'), ('Sólo presentación', 'Sólo presentación'),
                   ('No es necesario', 'No es necesario')],
        string=_('Servicio'), )
    x_especificacion_de_ceremonia = fields.Text(string="Especificación")

    x_audio_visual = fields.Many2many('event.audiovisual', string="Audio visual")
    x_especificacion_audio_visual = fields.Text(string="Especificación")

    x_equipo_extra = fields.Many2many('event.equipo.extra', string="Equipo extra")
    x_especificacion_equipo_extra = fields.Text(string="Especificación")

    x_servicio_fotografia = fields.Selection(
        selection=[('Toma panorámica de participantes', 'Toma panorámica de participantes'),
                   ('Tomas generales por el área', 'Tomas generales por el área'),
                   ('Foto profesional', 'Foto profesional'), ('No es necesario', 'No es necesario')],
        string=_('Servicio'), )
    x_especificacion_fotografia = fields.Text(string="Especificación")

    x_servicio_video = fields.Selection(
        selection=[('Toma fija, grabación simple de Co-Lab', 'Toma fija, grabación simple de Co-Lab'),
                   ('Video versión escenográfica sin edición', 'Video versión escenográfica sin edición'),
                   ('Video editado sólo con música', 'Video editado sólo con música'),
                   ('No es necesario', 'No es necesario')], string=_('Servicio'), )
    x_especificacion_video = fields.Text(string="Especificación")

    x_diseno = fields.Many2many('event.diseno', string="Diseño")
    x_especificacion_diseno = fields.Text(string="Especificación")

    x_articulos = fields.Many2many('event.articulos.promocionales', string="Articulos Promocionales")
    x_especificacion_articulos = fields.Text(string="Especificación")

    x_catering = fields.Many2many('event.catering', string="Catering")
    x_especificacion_catering = fields.Text(string="Especificación")

    x_facebook = fields.Char(string="Facebook")
    x_instagram = fields.Char(string="Instagram")
    x_linkedin = fields.Char(string="LinkedIn")
    x_twitter = fields.Char(string="Twitter")
    x_texto_descriptivo = fields.Text(string="Texto Descriptivo de redes sociales")

    x_encargado_de_bar = fields.Many2one('res.partner', string="Encargado de bar")
    x_encargado_de_cocina = fields.Many2one('res.partner', string="Encargado de cocina")
    x_encargado_de_mesa = fields.Many2one('res.partner', string="Encargado de mesa")

    x_ponentes = fields.Many2many('res.partner', 'event_ponentes_rel', string="Ponentes")
    x_especificacion_ponente = fields.Text(string="Especificación")

    @api.onchange('date_begin', 'date_end')
    def _hora_registro_y_salida(self):

        if self.is_online and self.date_begin and self.date_end:

            diferencia_de_fechas = self.date_end - self.date_begin
            evento_en_horas = diferencia_de_fechas.total_seconds() / 3600

            self.x_hora_de_registro = self.date_begin
            self.x_hora_de_salida = self.date_end
            self.x_duracion_del_evento = (evento_en_horas, 2)

        elif self.is_online is False and self.date_begin and self.date_end:

            hora_de_registro = self.date_begin - timedelta(hours=0, minutes=30)
            hora_de_salida = self.date_end + timedelta(hours=0, minutes=30)

            diferencia_de_fechas = hora_de_salida - hora_de_registro
            evento_en_horas = diferencia_de_fechas.total_seconds() / 3600

            self.x_hora_de_registro = hora_de_registro
            self.x_hora_de_salida = hora_de_salida
            self.x_duracion_del_evento = (evento_en_horas, 2)

    @api.onchange('x_hora_de_registro', 'x_hora_de_salida')
    def _hora_de_duracion(self):

        if self.x_hora_de_registro and self.x_hora_de_salida:
            diferencia_de_fechas = self.x_hora_de_salida - self.x_hora_de_registro
            evento_en_horas = diferencia_de_fechas.total_seconds() / 3600
            self.x_duracion_del_evento = round(evento_en_horas, 2)
