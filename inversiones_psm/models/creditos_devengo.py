from odoo import models, fields, api, _


class CreditosDevengos(models.Model):
    _name = 'inversion.credito.devengo'
    _rec_name = 'devengo'
    _description = "Devengo"

    devengo = fields.Char(string="Devengo")
    descripcion = fields.Char(string="Descripción")
