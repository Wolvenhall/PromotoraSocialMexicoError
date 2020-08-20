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
        if self.x_studio_cantidad > 70:
            self.x_studio_cantidad = 0
            return {'value': {},
                    'warning': {'title': 'Restricción', 'message': 'La capacidad maxima es de 70 personas.'}}
    
    @api.onchange('x_studio_inicio_del_evento')
    def _fecha_inicio(self):
    
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
            Organizacion = self.x_studio_organizadores
            EncargadoExterno = self.x_studio_nombre_1
            Catering = self.x_studio_requiere_servicio_de_catering
            
            # search record for area
            area = self.env['x_area'].search([('x_name', '=', 'CoLab')])
                
            vals = {
                'x_studio_field_YwP98': IdSolicitud,
                'name': NombreDelEvento,    
                'x_studio_solicitud_enviada_en': 'Tiempo',
                'x_studio_area': [(4, area.id)],
                'date_begin': FechaInicio,
                'date_end': FechaFin,
                'seats_min': MinimoPersonas,
                'seats_availability': 'limited',
                'seats_max': MaximoPersonas,
                'x_studio_requiere_catering': Catering
            }  
            
            new_event = request.env['event.event'].sudo().create(vals)
            
            # search record for approbal
            approbal = self.env['approval.request'].search([('id', '=', self.id)])

            # update status field
            approbal.write({'x_studio_evento_creado': datetime.now(),'x_studio_evento': new_event.id})
                
            print("Evento creado")

        else:
            raise Warning(_("Por favor verifique que todos los campos esten llenos"))

