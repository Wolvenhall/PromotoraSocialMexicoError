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
    
    @api.onchange('date_begin')
    def _hora_registro_y_salida(self):
        if is_online:    
            
            self.x_studio_hora_de_registro = self.date_begin
            self.x_studio_hora_de_salida = self.date_end
            
            diferencia_de_fechas = self.x_studio_hora_de_salida - self.x_studio_hora_de_registro
            evento_en_horas = diferencia_de_fechas.total_seconds() / 3600                       
            self.x_studio_duracion_del_evento = evento_en_horas
            
        else:
            hora_de_registro = self.date_begin - timedelta(hours=0, minutes=30)
            hora_de_salida = self.date_end + timedelta(hours=0, minutes=30)
            
            diferencia_de_fechas = hora_de_salida - hora_de_registro
            evento_en_horas = diferencia_de_fechas.total_seconds() / 3600
            
            self.x_studio_hora_de_registro = hora_de_registro
            self.x_studio_hora_de_salida = hora_de_salida            
            self.x_studio_duracion_del_evento = evento_en_horas
            
    @api.onchange('x_studio_hora_de_registro', 'x_studio_hora_de_salida')
    def _hora_de_duracion(self):
        
        if self.x_studio_hora_de_registro and self.x_studio_hora_de_salida:
            diferencia_de_fechas = self.x_studio_hora_de_salida - self.x_studio_hora_de_registro
            evento_en_horas = diferencia_de_fechas.total_seconds() / 3600                       
            self.x_studio_duracion_del_evento = evento_en_horas
        