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

    # @api.onchange('x_studio_personas_proyectadas')
    # def _capacidad_maxima(self):
    #     if self.x_studio_personas_proyectadas > 70:
    #         self.x_studio_personas_proyectadas = 0
    #         return {'value': {},
    #                 'warning': {'title': 'Restricción', 'message': 'La capacidad maxima es de 70 personas.'}}
    #
    # @api.onchange('x_studio_inicio_de_evento')
    # def _fecha_inicio(self):
    #
    #     two_weeks = datetime.now() + timedelta(days=14)
    #
    #     star_date_format = two_weeks
    #     two_weeks_format = self.x_studio_inicio_de_evento
    #
    #     if self.x_studio_inicio_de_evento:
    #         if star_date_format > two_weeks_format:
    #             self.x_studio_inicio_de_evento = False
    #             self.x_studio_fin_de_evento = False
    #             return {'value': {},
    #                     'warning': {'title': 'Restricción',
    #                                 'message': 'Seleccione una fecha despues del ' + two_weeks.strftime("%d/%m/%Y")}
    #                     }

#
#
# _sql_constraints = [('capacidad_maxima', 'CHECK (x_studio_personas_proyectadas>=1)',
# 'All product quantities must be greater or equal to 0.')]
#
# class ApprovalRequest(models.Model):
#     _inherit = "approval.request"
#
#     def create_event(self):
#
#         if self.x_studio_nombre_evento:
#
#             vals = {
#                 'name': self.x_studio_nombre_evento,
#                 'organizer_id': self.x_studio_organizacin_que_invita.id,
#                 'user_id': self.x_studio_host.id,
#                 'date_begin': self.x_studio_inicio_de_evento,
#                 'date_end': self.x_studio_fin_de_evento,
#                 # 'seats_min': rec['reason'],
#                 'seats_availability': 'limited',
#                 'seats_max': self.x_studio_personas_proyectadas
#             }
#
#             try:
#                 # 1. Create new Request
#                 new_event = request.env['event.event'].sudo().create(vals)
#                 print(vals)
#             except Exception as e:
#                 print("Exception: ", e)
#
#         else:
#             raise Warning(_("Por favor verifique que todos los campos esten llenos"))
