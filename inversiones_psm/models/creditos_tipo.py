from odoo import models, fields, api, _


class CreditosTipo(models.Model):
    _name = 'inversion.credito.tipo'
    _rec_name = 'tipo'
    _description = "Tipo"

    tipo = fields.Char(string="Tipo")
    descripcion = fields.Char(string="Descripción")
