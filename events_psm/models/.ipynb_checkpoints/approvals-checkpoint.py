import requests
import base64
from odoo import models, api, _, fields
from datetime import datetime
from datetime import date
from odoo.http import request
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import timedelta
from odoo import modules


class ApprovalRequest(models.Model):
    _inherit = "approval.request"

    def _default_lineamiento_id(self):
        return self.env['approval.lineamiento'].search([('id', '=', '1')], limit=1)

    x_lineamiento = fields.Many2one('approval.lineamiento', string="Lineamiento",
                                    default=_default_lineamiento_id)
    x_estoy_de_acuerdo = fields.Selection(selection=[('si', 'Sí'), ('no', 'No'), ], string=_('¿Esta de acuerdo?'),)

    x_tipo_del_evento = fields.Selection(selection=[('presencial', 'Presencial'), ('enlinea', 'En Línea'), ],
                                        string=_('Tipo de evento'), default="presencial")
    
    x_nombre_del_evento = fields.Char(string="Nombre del evento")
    x_objetivo = fields.Text(string="Objetivo")

    x_organizadores = fields.Many2many('res.partner', string="Organizadores")

    x_fecha_del_evento = fields.Date(string="Fecha del evento")

    x_hora_de_inicio = fields.Float(string="Hora de inicio")
    x_hora_de_fin = fields.Float(string="Hora de fin")

    x_cantidad = fields.Integer(string="Cantidad")

    x_colaborador = fields.Many2one('hr.employee', string="Host PSM")
    x_departamento = fields.Char(string='Departamento', related='x_colaborador.department_id.name')

    x_encargado_externo = fields.Many2one('res.partner', string="Encargado externo")
    x_correo_electronico = fields.Char(string="Correo electrónico", related='x_encargado_externo.email')
    x_movil = fields.Char(string="Móvil", related='x_encargado_externo.mobile')

    x_quien_paga_el_evento = fields.Selection(selection=[('Interno', 'Interno'),
                                                         ('Externo', 'Externo'),
                                                         ('Ambos', 'Ambos')],
                                              string=_('¿Quien paga el evento?'))

    x_porcentaje_que_paga_psm = fields.Float(string="Porcentaje que paga PSM")
    x_requiere_servicio_de_catering = fields.Selection(selection=[('si', 'Sí'), ('no', 'No')],
                                                       string=_('¿Requiere servicio de catering?'))

    x_brigadista = fields.Many2one('hr.employee', string="Brigadista")
    x_cordinador = fields.Many2one('hr.employee', string="Coordinador")
    x_evento = fields.Many2one('event.event', string="Evento")
    x_evento_creado = fields.Datetime(string="Evento creado el")

    x_fecha_de_solicitud = fields.Datetime(string="Fecha de solicitud")

    @api.onchange('x_cantidad')
    def _capacidad_maxima(self):
        if self.x_tipo_del_evento == 'presencial':
            if self.x_cantidad > 70:
                self.x_cantidad = 0
                return {'value': {},
                        'warning': {'title': 'Restricción', 'message': 'La capacidad maxima es de 70 personas.'}}

    @api.onchange('x_tipo_del_evento')
    def _borrar_datos(self):
        if self.x_tipo_del_evento == 'presencial':
            self.x_cantidad = 0
            self.x_hora_de_inicio = False
            self.x_hora_de_fin = False
        elif self.x_tipo_del_evento == 'enlinea':
            self.x_cantidad = 0
            self.x_hora_de_inicio = False
            self.x_hora_de_fin = False
            self.x_requiere_servicio_de_catering = 'no'

    @api.onchange('x_fecha_del_evento')
    def _fecha_del_evento(self):
        if self.x_tipo_del_evento == 'presencial':
            two_weeks = date.today() + timedelta(days=14)

            star_date_format = two_weeks
            two_weeks_format = self.x_fecha_del_evento

            if self.x_fecha_del_evento:
                if star_date_format > two_weeks_format:
                    self.x_fecha_del_evento = False
                    return {'value': {},
                            'warning': {'title': 'Restricción',
                                        'message': 'Seleccione una fecha despues del ' + two_weeks.strftime("%d/%m/%Y")}
                            }

    @api.onchange('x_hora_de_inicio', 'x_hora_de_fin')
    def _formato_de_horas(self):
        if self.x_hora_de_inicio > 24:
            self.x_hora_de_inicio = 0
            return {'value': {},
                    'warning': {'title': 'Restricción',
                                'message': 'El formato de fecha debe ser de 24 hrs'}
                    }
        if self.x_hora_de_fin > 24:
            self.x_hora_de_fin = 0
            return {'value': {},
                    'warning': {'title': 'Restricción',
                                'message': 'El formato de fecha debe ser de 24 hrs'}
                    }
        if self.x_hora_de_inicio == 0:
            self.x_hora_de_fin = 0

    @api.onchange('x_hora_de_inicio')
    def _diferencia_de_hora_inicio(self):
        if self.x_hora_de_fin > 0:
            if self.x_hora_de_inicio > self.x_hora_de_fin:
                self.x_hora_de_inicio = 0
                self.x_hora_de_fin = 0
                return {'value': {},
                        'warning': {'title': 'Restricción',
                                    'message': 'La hora de inicio no puede ser mayor a la hora de fin por favor use el formato de 24 hrs.'}
                        }

    @api.onchange('x_hora_de_fin')
    def _diferencia_de_hora_fin(self):
        if self.x_hora_de_inicio > self.x_hora_de_fin:
            self.x_hora_de_fin = 0
            return {'value': {},
                    'warning': {'title': 'Restricción',
                                'message': 'La hora de inicio no puede ser mayor a la hora de fin por favor use el formato de 24 hrs.'}
                    }

    def create_event(self):

        if self.x_cordinador.id is False:
            raise Warning(_("Por favor agregue al Coordinador para poder crear el evento"))

        elif self.x_brigadista.id is False:
            raise Warning(_("Por favor agregue al Brigadista para poder crear el evento"))

        else:
            IdSolicitud = self.id
            NombreDelEvento = self.x_nombre_del_evento
            FechaInicio = self.x_fecha_del_evento
            FechaFin = self.x_fin_del_evento
            MaximoPersonas = self.x_cantidad
            organizaciones = self.x_organizadores
            Catering = self.x_requiere_servicio_de_catering
            TipoDeEvento = self.x_tipo_del_evento
            Coordinador = self.x_cordinador
            Brigadista = self.x_brigadista

            hora_de_registro = FechaInicio - timedelta(hours=0, minutes=30)
            hora_de_salida = FechaFin + timedelta(hours=0, minutes=30)

            diferencia_de_fechas = hora_de_salida - hora_de_registro
            evento_en_horas = diferencia_de_fechas.total_seconds() / 3600

            if TipoDeEvento == 'En linea':
                EsEnLinea = True
                TipoEvento = 1
            else:
                EsEnLinea = False
                TipoEvento = 2

            area = self.env['event.area'].search([('name', '=', 'CoLab')])

            vals = {
                'x_solicitud_de_evento': IdSolicitud,
                'name': NombreDelEvento,
                'x_solicitud_enviada_en': 'tiempo',
                'x_area': [(4, area.id)],
                'date_begin': FechaInicio,
                'date_end': FechaFin,
                'seats_min': 0,
                'seats_availability': 'limited',
                'seats_max': MaximoPersonas,
                'x_requiere_catering': Catering,
                'x_hora_de_registro': hora_de_registro,
                'x_hora_de_salida': hora_de_salida,
                'is_online': EsEnLinea,
                'x_duracion_del_evento': evento_en_horas,
                'event_type_id': TipoEvento,
                'x_organizadores': [(6, 0, organizaciones.ids)],
                'x_coordinador': Coordinador.id,
                'x_brigadista': Brigadista.id
            }

            new_event = request.env['event.event'].sudo().create(vals)

            if new_event.id:
                if Coordinador:
                    employee_id = self.env['hr.employee'].search([('id', '=', Coordinador.id)])
                    if employee_id:
                        user_id = self.env['res.users'].search([('id', '=', employee_id.user_id.id)])
                        if user_id:
                            self._crear_seguidor(new_event.id, 'event.event', user_id.partner_id.id)

                if Brigadista:
                    employee_id = self.env['hr.employee'].search([('id', '=', Brigadista.id)])
                    if employee_id:
                        user_id = self.env['res.users'].search([('id', '=', employee_id.user_id.id)])
                        if user_id:
                            self._crear_seguidor(new_event.id, 'event.event', user_id.partner_id.id)

            # search record for approbal
            approbal = self.env['approval.request'].search([('id', '=', self.id)])

            # update status field
            approbal.write({'x_evento_creado': datetime.now(), 'x_evento': new_event.id})

            print("Evento creado")

    def _crear_seguidor(self, res_id, model, partner_id):
        follower_id = False
        reg = {
            'res_id': res_id,
            'res_model': model,
            'partner_id': partner_id
        }
        try:
            follower_id = self.env['mail.followers'].create(reg)
        except Exception as e:
            print("Exception: ", e)

