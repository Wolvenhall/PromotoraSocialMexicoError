from odoo import models, fields


class Lineamiento(models.Model):
    _name = "approval.lineamiento"
    _rec_name = 'name'
    _description = "Lineamientos"

    name = fields.Text('Nombre del Lineamiento')
    lineamiento = fields.Binary(string="Documento de Lineamiento")
