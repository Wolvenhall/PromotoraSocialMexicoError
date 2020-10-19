# -*- coding: utf-8 -*-
from odoo import models, fields, api


class Sector(models.Model):
    _name = 'account.move.sector'
    _rec_name = 'sector'
    _description = "Sector"

    sector = fields.Text(string="Sector")


class SubsSector(models.Model):
    _name = 'account.move.subsector'
    _rec_name = 'subsector'
    _description = "Subsector"

    subsector = fields.Text(string="Subsector")


class TipoDeComprobante(models.Model):
    _name = 'account.move.tipo.comprobante'
    _rec_name = 'tipo_de_coprobante'
    _description = "Tipo de comprobante"

    tipo_de_coprobante = fields.Text(string="Tipo de comprobante")


class Proyecto(models.Model):
    _name = 'proyecto'
    _rec_name = 'proyecto'
    _description = "Proyecto"

    proyecto = fields.Text(string="Proyecto")
    salesforce_id = fields.Integer(string="Id Salesforce")


class CentroDeCosto(models.Model):
    _name = 'account.move.centro.de.costos'
    _rec_name = 'centro_de_costos'
    _description = "Centro de costos"

    centro_de_costos = fields.Text(string="Centro de costos")


class FormaDePago(models.Model):
    _name = 'account.move.forma.de.pago'
    _rec_name = 'forma_de_pago'
    _description = "Forma de Pago"

    forma_de_pago = fields.Text(string="Forma de pago")
