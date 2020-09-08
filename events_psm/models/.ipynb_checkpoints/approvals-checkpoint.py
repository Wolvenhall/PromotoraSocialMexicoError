import requests
import base64
from odoo import models, api, _, fields
from datetime import datetime
from odoo.http import request
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import timedelta
from odoo import modules


class ApprovalRequest(models.Model):
    _inherit = "approval.request"
    
    def _default_lineamiento_id(self):
        return self.env['x_lineamientos'].search([('id', '=', '1')], limit=1)
    
    x_studio_lineamiento = fields.Many2one('x_lineamientos',string="Lineamiento de uso CoLab",default=_default_lineamiento_id)

    @api.onchange('x_studio_cantidad')
    def _capacidad_maxima(self):        
        if self.x_studio_tipo_de_evento == 'Presencial':
            if self.x_studio_cantidad > 70:
                self.x_studio_cantidad = 0
                return {'value': {},
                        'warning': {'title': 'Restricción', 'message': 'La capacidad maxima es de 70 personas.'}}
    
    @api.onchange('x_studio_tipo_de_evento')
    def _borrar_datos(self):
        if self.x_studio_tipo_de_evento == 'Presencial':
            self.x_studio_cantidad = 0
            self.x_studio_inicio_del_evento = False
            self.x_studio_fin_del_evento = False
        elif self.x_studio_tipo_de_evento == 'En linea':
            self.x_studio_cantidad = 0
            self.x_studio_inicio_del_evento = False
            self.x_studio_fin_del_evento = False
            self.x_studio_requiere_servicio_de_catering = 'No'
                   
    @api.onchange('x_studio_inicio_del_evento')
    def _fecha_inicio(self):
        if self.x_studio_tipo_de_evento == 'Presencial':    
            two_weeks = datetime.now() + timedelta(days=14)
    
            star_date_format = two_weeks
            two_weeks_format = self.x_studio_inicio_del_evento

            if self.x_studio_inicio_del_evento:
                if star_date_format > two_weeks_format:
                    self.x_studio_inicio_del_evento = False
                    self.x_studio_fin_del_evento = False
                    return {'value': {},
                            'warning': {'title': 'Restricción',
                                        'message': 'Seleccione una fecha despues del ' + two_weeks.strftime("%d/%m/%Y")}
                            }
    
    def create_event(self):

        if self.id:     
            
            IdSolicitud = self.id
            Solicitante = self.request_owner_id
            NombreDelEvento = self.x_studio_nombre_del_evento
            Objetivo = self.x_studio_objetivo
            FechaInicio = self.x_studio_inicio_del_evento
            FechaFin = self.x_studio_fin_del_evento
            MinimoPersonas = 0
            MaximoPersonas = self.x_studio_cantidad
            HostPSM = self.x_studio_nombre
            organizaciones = self.x_studio_organizadores
            EncargadoExterno = self.x_studio_nombre_1
            Catering = self.x_studio_requiere_servicio_de_catering
            TipoDeEvento = self.x_studio_tipo_de_evento
            Coordinador = self.x_studio_coordindor
            Brigadista = self.x_studio_brigadista
            
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
            
            area = self.env['x_area'].search([('x_name', '=', 'CoLab')])
                
            vals = {
                'x_studio_field_YwP98': IdSolicitud,
                'name': NombreDelEvento,    
                'x_studio_solicitud_enviada_en': 'Tiempo',
                'x_studio_area': [(4, area.id)],
                'date_begin': FechaInicio,
                'date_end': FechaFin,
                'seats_min': 0,
                'seats_availability': 'limited',
                'seats_max': MaximoPersonas,
                'x_studio_requiere_catering': Catering,
                'x_studio_hora_de_registro': hora_de_registro,
                'x_studio_hora_de_salida': hora_de_salida,
                'is_online': EsEnLinea,
                'x_studio_duracion_del_evento': evento_en_horas,
                'event_type_id': TipoEvento,
                'x_studio_organizadores_2': [(6, 0, organizaciones.ids)],
                'x_studio_coordinador': Coordinador.id,
                'x_studio_brigadista': Brigadista.id
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
            approbal.write({'x_studio_evento_creado': datetime.now(),'x_studio_evento': new_event.id})
                
            print("Evento creado")

        else:
            raise Warning(_("Por favor verifique que todos los campos esten llenos"))
            
            
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
    