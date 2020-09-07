from odoo import models, api, _, fields


class TablaVacaciones(models.Model):
    _name = 'tabla.vacaciones'
    _description = "Tabla Vacaciones"

    form_id = fields.Many2one('tabla.nomina', string='Tabla Nómina')
    antiguedad_minima = fields.Float('Antigüedad minima')
    antiguedad_maxima = fields.Float('Antigüedad maxima')
    dias_vacaciones = fields.Float('Dias Vacaciones')
    

class TablaEfectosCotizacion(models.Model):
    _name = 'tabla.efectos.cotizacion'
    _description = "Tabla para Efectos de Cotización"

    form_id = fields.Many2one('tabla.nomina', string='Tabla Nómina')
    antiguedad_minima = fields.Float('Antigüedad minima')
    antiguedad_maxima = fields.Float('Antigüedad maxima')
    dias_vacaciones = fields.Float('Dias Vacaciones')


class TablaISR(models.Model):
    _name = 'tabla.isr'
    _description = "Tabla ISR"

    form_id = fields.Many2one('tabla.nomina', string='Tabla Nómina')
    limite_inferior = fields.Float('Límite inferior')
    limite_superior = fields.Float('Límite superior')
    cuota_fija = fields.Float('Cuota fija')
    exedente = fields.Float('Exedente')


class TablaSubsidioEmpleo(models.Model):
    _name = 'tabla.subsidio.empleo'
    _description = "Tabla Subsidio Empleo"

    form_id = fields.Many2one('tabla.nomina', string='Tabla Nómina')
    limite_inferior = fields.Float('Límite inferior')
    limite_superior = fields.Float('Límite superior')
    credito = fields.Float('Crédito')


class TablaNomina(models.Model):
    _name = 'tabla.nomina'
    _description = "Tabla Nomina"

    # one2many
    dias_de_vacaciones = fields.One2many('tabla.vacaciones', 'form_id', copy=True)
    isr = fields.One2many('tabla.isr', 'form_id', copy=True)
    subsidio_para_el_empleo = fields.One2many('tabla.subsidio.empleo', 'form_id', copy=True)
    tabla_efectos_cotizacion = fields.One2many('tabla.efectos.cotizacion', 'form_id', copy=True)

    # Fields
    name = fields.Text('Año')
    uma = fields.Float('UMA')
    salario_minimo = fields.Float('Salario minimo')
    periodo_mensual_en_dias = fields.Float('Periodo Mensual (Dias)')

    porcentaje_prima_vacacional = fields.Float('Prima vacacional (%)', 0.00)
    porcentaje_prima_de_riesgo = fields.Float('Prima de riesgo (%)')
    limite_inv_y_vid_y_cv = fields.Float('Límite inv y vid y cv')
    salario_minimo_vigente = fields.Float('Salario minimo vigente')

    # CESANTIA Y VEJEZ
    cesantia_y_vejez_patron = fields.Float('Patron')
    cesantia_y_vejez_total = fields.Float('Total', digits=(12, 3))
    cesantia_y_vejez_trabajador = fields.Float('Trabajador')

    # CUOTA FIJA
    cuota_fija_patron = fields.Float('Patron')
    cuota_fija_total = fields.Float('Total')
    cuota_fija_trabajador = fields.Float('Trabajador')

    # EXEDENTE
    excedente_patron = fields.Float('Patron')
    excedente_total = fields.Float('Total')
    excedente_trabajador = fields.Float('Trabajador')

    # GASTOS MEDICOS
    gastos_medicos_pensionados_patron = fields.Float('Patron')
    gastos_medicos_pensionados_total = fields.Float('Total', digits=(12, 3))
    gastos_medicos_pensionados_trabajador = fields.Float('Trabajador')

    # GUARDERIAS Y GASTOS
    guarderias_y_gastos_de_prevision_social_patron = fields.Float('Patron')
    guarderias_y_gastos_de_prevision_social_total = fields.Float('Total')
    guarderias_y_gastos_de_prevision_social_trabajador = fields.Float('Trabajador')

    # INFONAVIT
    infonavit_patron = fields.Float('Patron')
    infonavit_total = fields.Float('Total')
    infonavit_trabajador = fields.Float('Trabajador')

    # INVALIDEZ Y VIDA
    invalidez_y_vida_patron = fields.Float('Patron')
    invalidez_y_vida_total = fields.Float('Total', digits=(12, 3))
    invalidez_y_vida_trabajador = fields.Float('Trabajador')

    # PRESTACIONES DE DINERO
    prestaciones_en_dinero_patron = fields.Float('Patron')
    prestaciones_en_dinero_total = fields.Float('Exedente')
    prestaciones_en_dinero_trabajador = fields.Float('Trabajador')

    # RETIRO
    retiro_patron = fields.Float('Retiro patron')
    retiro_total = fields.Float('Retiro total')
    retiro_trabajador = fields.Float('Retiro trabajador')

    @api.onchange('cesantia_y_vejez_patron', 'cesantia_y_vejez_trabajador')
    def _change_cesantia_y_vejez_total(self):
        self.cesantia_y_vejez_total = self.cesantia_y_vejez_patron + self.cesantia_y_vejez_trabajador

    @api.onchange('cuota_fija_patron', 'cuota_fija_trabajador')
    def _change_cuota_fija_total(self):
        self.cuota_fija_total = self.cuota_fija_patron + self.cuota_fija_trabajador

    @api.onchange('excedente_patron', 'excedente_trabajador')
    def _change_excedente_total(self):
        self.excedente_total = self.excedente_patron + self.excedente_trabajador

    @api.onchange('gastos_medicos_pensionados_patron', 'gastos_medicos_pensionados_trabajador')
    def _change_gastos_medicos_pensionados_total(self):
        self.gastos_medicos_pensionados_total = self.gastos_medicos_pensionados_patron + self.gastos_medicos_pensionados_trabajador

    @api.onchange('guarderias_y_gastos_de_prevision_social_patron',
                  'guarderias_y_gastos_de_prevision_social_trabajador')
    def _change_guarderias_y_gastos_de_prevision_social_total(self):
        self.guarderias_y_gastos_de_prevision_social_total = self.guarderias_y_gastos_de_prevision_social_patron + self.guarderias_y_gastos_de_prevision_social_trabajador

    @api.onchange('infonavit_patron', 'infonavit_trabajador')
    def _change_infonavit_total(self):
        self.infonavit_total = self.infonavit_patron + self.infonavit_trabajador

    @api.onchange('invalidez_y_vida_patron', 'invalidez_y_vida_trabajador')
    def _change_invalidez_y_vida_total(self):
        self.invalidez_y_vida_total = self.invalidez_y_vida_patron + self.invalidez_y_vida_trabajador

    @api.onchange('prestaciones_en_dinero_patron', 'prestaciones_en_dinero_trabajador')
    def _change_prestaciones_en_dinero_total(self):
        self.prestaciones_en_dinero_total = self.prestaciones_en_dinero_patron + self.prestaciones_en_dinero_trabajador

    @api.onchange('retiro_patron', 'retiro_trabajador')
    def _change_retiro_total(self):
        self.retiro_total = self.retiro_patron + self.retiro_trabajador