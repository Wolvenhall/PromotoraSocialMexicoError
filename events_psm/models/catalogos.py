from odoo import models, fields


class ArticulosPromocionales(models.Model):
    _name = "event.articulos.promocionales"
    _rec_name = 'name'
    _description = "Articulos Promocionales"

    name = fields.Text('Articulo')
    description = fields.Text(string="Descripción")


class Audiovisual(models.Model):
    _name = "event.audiovisual"
    _rec_name = 'name'
    _description = "Audio Visual"

    name = fields.Text('Audio visual')
    description = fields.Text(string="Descripción")


class Catering(models.Model):
    _name = "event.catering"
    _rec_name = 'name'
    _description = "Catering"

    name = fields.Text('Menú')
    product = fields.Many2many('product.product', string="Producto")


class Diseno(models.Model):
    _name = "event.diseno"
    _rec_name = 'name'
    _description = "Diseño"

    name = fields.Text('Diseño')
    description = fields.Text(string="Descripción")


class Distribucion(models.Model):
    _name = "event.distribucion"
    _rec_name = 'name'
    _description = "Distribución"

    name = fields.Text('Distribución')
    capacity = fields.Integer('Capacidad Máxima')
    image = fields.Binary('Imagen')
    description = fields.Text(string="Descripción")


class EquipoExtra(models.Model):
    _name = "event.equipo.extra"
    _rec_name = 'name'
    _description = "Equipo extra"

    name = fields.Text('Equipo extra')
    description = fields.Text(string="Descripción")


class Audiencia(models.Model):
    _name = "event.audiencia"
    _rec_name = 'name'
    _description = "Audiencia"

    name = fields.Text('Audiencia')
    description = fields.Text(string="Descripción")


class Area(models.Model):
    _name = "event.area"
    _rec_name = 'name'
    _description = "Área"

    name = fields.Text('Área')
    description = fields.Text(string="Descripción")


class EtiquetaCatering(models.Model):
    _name = "event.etiqueta.catering"
    _rec_name = 'name'
    _description = "Etiqueta catering"

    name = fields.Text('Etiqueta catering')


class ProductProduct(models.Model):
    _inherit = "product.template"

    x_etiqueta_catering = fields.Many2many('event.etiqueta.catering', string="Etiqueta catering")