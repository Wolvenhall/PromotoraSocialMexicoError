import requests
import base64
from odoo import models, api, _, fields
from datetime import datetime, date
from odoo.http import request
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import timedelta
from odoo import modules


def message(titulo, mensaje):
    return {'value': {}, 'warning': {'title': titulo, 'message': mensaje}}


class PurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    x_evento_id = fields.Many2one('event.event', string="Evento")


class PurchaseRequisitionInherit(models.Model):
    _inherit = "purchase.requisition"

    x_evento_id = fields.Many2one('event.event', string="Evento")


class Event(models.Model):
    _inherit = "event.event"

#     def _duracion_horas(self):
#         if self.x_hora_de_registro > 0 and self.x_hora_maxima_de_salida > 0:
#             diferencia_de_fechas = self.x_hora_maxima_de_salida - self.x_hora_de_registro
#             self.x_duracion_del_evento = round(diferencia_de_fechas, 2)

    def muestra_compras(self):
        return {
            'name': _('Compras'),
            'domain': [('x_evento_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'purchase.order',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def muestra_licitaciones(self):
        return {
            'name': _('Licitaciones'),
            'domain': [('x_evento_id', '=', self.id)],
            'view_type': 'form',
            'res_model': 'purchase.requisition',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def obten_total_compras(self):
        total = self.env['purchase.order'].search_count([('x_evento_id', '=', self.id)])
        self.x_conteo_compras = total

    def obten_total_licitaciones(self):
        total = self.env['purchase.requisition'].search_count([('x_evento_id', '=', self.id)])
        self.x_conteo_licitaciones = total

    x_conteo_compras = fields.Integer(string="Compras", compute="obten_total_compras")
    x_conteo_licitaciones = fields.Integer(string="Licitaciones", compute="obten_total_licitaciones")

    x_solicitud_de_evento = fields.Many2one('approval.request', string="Solicitud")
    x_solicitud_enviada_en = fields.Selection(selection=[('tiempo', 'Tiempo'), ('destiempo', 'Destiempo'), ],
                                              string=_('Puntualidad'), )
    x_solicitante = fields.Char(string="Solicitante", related='x_solicitud_de_evento.request_owner_id.name')
    x_objetivo = fields.Text(string="Objetivo", related='x_solicitud_de_evento.x_objetivo')
    x_descripcion = fields.Text(string="Descripción", related='x_solicitud_de_evento.reason')
    x_invitados_proyectados = fields.Integer(string="Invitados proyectados", required=True)

    x_host = fields.Many2one(string="Host", related='x_solicitud_de_evento.x_colaborador')
    x_departamento = fields.Char(string='Departamento', related='x_solicitud_de_evento.x_departamento')
    x_organizadores = fields.Many2many('res.partner', 'event_organizadores_rel', string="Organizadores")
    x_quien_paga_el_evento = fields.Selection(
        selection=[('Interno', 'Interno'), ('Externo', 'Externo'), ('Ambos', 'Ambos')],
        string=_('¿Quien paga el evento?'), )
    x_porcentaje_que_paga_psm = fields.Float(string="% que paga PSM",
                                             related='x_solicitud_de_evento.x_porcentaje_que_paga_psm')
    x_audiencia = fields.Many2many('event.audiencia', string="Audiencia")
    x_relacion = fields.Many2many('event.relacion', string="Relacion")

    x_area = fields.Many2many('event.area', string="Área")
    x_coordinador = fields.Many2one(string="Coordinador", related='x_solicitud_de_evento.x_cordinador')
    x_brigadista = fields.Many2one(string="Brigadista", related='x_solicitud_de_evento.x_brigadista')

    x_tipo_de_evento = fields.Selection(
        selection=[('cerrado', 'Cerrado / Privado sólo para invitados'),
                   ('abierto', 'Abierto para colaboradores')], string=_('Tipo de evento'), )

    x_categoria_de_evento = fields.Many2many('event.categoria', string="Categoria del evento")

    x_colaboradores_adicionales = fields.Integer(string="Colaboradores Adicionales")
    x_requiere_catering = fields.Selection(selection=[('si', 'Sí'), ('no', 'No'), ], string=_('¿Requiere catering?'), )
    x_budget_proyectado = fields.Float(string="Budget proyectado")

    x_fecha_de_solicitud = fields.Date(string="Fecha de solicitud",
                                           related='x_solicitud_de_evento.x_fecha_de_solicitud')
    x_fecha_del_evento = fields.Date(string="Fecha del evento", required=True)

    x_hora_de_registro = fields.Float(string="Hora registro", required=True)
    x_hora_inicio_del_evento = fields.Float(string="Hora inicio", required=True)
    x_hora_fin_del_evento = fields.Float(string="Hora fin", required=True)
    x_hora_maxima_de_salida = fields.Float(string="Hora salida", required=True)

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
    x_otros = fields.Char(string="Otros")
    x_texto_descriptivo = fields.Text(string="Texto Descriptivo de redes sociales")

    x_encargado_de_bar = fields.Many2one('res.partner', string="Encargado de bar")
    x_encargado_de_cocina = fields.Many2one('res.partner', string="Encargado de cocina")
    x_encargado_de_mesa = fields.Many2one('res.partner', string="Encargado de mesa")

    x_ponentes = fields.Many2many('res.partner', 'event_ponentes_rel', string="Ponentes")
    x_especificacion_ponente = fields.Text(string="Especificación")

    x_incidencia = fields.Text(string="Incidencias")

    @api.onchange('x_invitados_proyectados')
    def _invitados_proyectados(self):
        if self.x_invitados_proyectados > 0:
            self.seats_availability = 'limited'
            self.seats_max = self.x_invitados_proyectados
        else:
            self.seats_availability = 'unlimited'
            self.seats_max = 0

    @api.onchange('x_hora_inicio_del_evento', 'x_hora_fin_del_evento', 'x_hora_maxima_de_salida', 'x_hora_de_registro')
    def _formato_de_horas(self):
        if self.x_hora_inicio_del_evento > 24:
            self.x_hora_inicio_del_evento = 0
            return {'value': {},
                    'warning': {'title': 'Restricción',
                                'message': 'El formato de fecha debe ser de 24 hrs'}
                    }
        if self.x_hora_fin_del_evento > 24:
            self.x_hora_fin_del_evento = 0
            return {'value': {},
                    'warning': {'title': 'Restricción',
                                'message': 'El formato de fecha debe ser de 24 hrs'}
                    }
        if self.x_hora_maxima_de_salida > 24:
            self.x_hora_maxima_de_salida = 0
            return {'value': {},
                    'warning': {'title': 'Restricción',
                                'message': 'El formato de fecha debe ser de 24 hrs'}
                    }
        if self.x_hora_de_registro > 24:
            self.x_hora_de_registro = 0
            return {'value': {},
                    'warning': {'title': 'Restricción',
                                'message': 'El formato de fecha debe ser de 24 hrs'}
                    }
        if self.x_hora_inicio_del_evento == 0:
            self.x_hora_fin_del_evento = 0

    @api.onchange('x_hora_maxima_de_salida')
    def _calculo_fecha_evento(self):
        if self.x_hora_maxima_de_salida > 0:

            if self.x_fecha_del_evento is False:
                self.x_hora_maxima_de_salida = 0
                return message('Restricción', 'Por favor agregue la fecha del evento')

            elif self.x_hora_de_registro == 0:
                self.x_hora_maxima_de_salida = 0
                return message('Restricción', 'Por favor agregue la hora de registro')

            elif self.x_hora_inicio_del_evento == 0:
                self.x_hora_maxima_de_salida = 0
                return message('Restricción', 'Por favor agregue la hora de inicio del evento')

            elif self.x_hora_fin_del_evento == 0:
                self.x_hora_maxima_de_salida = 0
                return message('Restricción', 'Por favor agregue la hora de fin del evento')

            elif self.x_hora_de_registro > self.x_hora_inicio_del_evento:
                self.x_hora_maxima_de_salida = 0
                return message('Restricción', 'La hora de registro no puede ser mayor a la hora de inicio')

            elif self.x_hora_inicio_del_evento > self.x_hora_fin_del_evento:
                self.x_hora_maxima_de_salida = 0
                return message('Restricción', 'La hora de inicio no puede ser mayor a la hora de fin por favor use el '
                                              'formato de 24 hrs')

            elif self.x_hora_fin_del_evento > self.x_hora_maxima_de_salida:
                self.x_hora_maxima_de_salida = 0
                return message('Restricción', 'La hora de fin del evento no puede ser mayor a la hora de salida maxima')

            elif self.x_hora_de_registro > 0 and self.x_hora_inicio_del_evento > 0 and self.x_hora_fin_del_evento > 0:

                tiempo = datetime.min.time()
                fecha = datetime.combine(self.x_fecha_del_evento, tiempo)

                horas_registro, minutos_registro = divmod(self.x_hora_de_registro + 5, 1)
                horas_salida, minutos_salida = divmod(self.x_hora_maxima_de_salida + 5, 1)

                horas_registro = timedelta(hours=horas_registro, minutes=minutos_registro)
                horas_salida = timedelta(hours=horas_salida, minutes=minutos_salida)

                fecha_de_inicio = fecha + horas_registro
                self.date_begin = fecha_de_inicio

                fecha_de_fin = fecha + horas_salida
                self.date_end = fecha_de_fin
