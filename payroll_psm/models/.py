import requests
import base64
from odoo import models, api, _, fields
from datetime import datetime, date
import time
import calendar
from odoo.http import request
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import timedelta
from odoo import modules


class HrContract(models.Model):
    _inherit = "hr.contract"

    # NUEVOS CAMPOS EN MODULO DE CONTRATOS

    # DATOS DE SALIDA
    departure_reason = fields.Selection(
        selection=[('voluntario', 'Voluntario'),
                   ('involuntario', 'Involuntario'),
                   ('retiro', 'Retiro'), ],
        string=_('Razón de salida'))
    departure_description = fields.Text('Motivo de salida')

    # VALORES DE ENTRADA
    
    tabla_nomina = fields.Many2one('tabla.nomina', 'Tabla nomina',
                                   help="Tabla de configuraciones con la cual se realizaran los calulos")
    fecha_antiguedad = fields.Date(string=_('Fecha de antiguedad'), help="Fecha utilizada para generar calculos")

    # CALCULOS

    ingreso_anual = fields.Float('Ingreso anual', 0.00, help="(Ingreso mensual) x 12")
    salario_diario = fields.Float('Salario diario', 0.00, help="(Ingreso mensual) / 30")
    ingreso_variable_mensual = fields.Float('Ingreso variable mensual', 0.00,
                                            help="SI (Ingreso anual9 > ((UMA) * (Dias mes)) ENTONCES ((UMA) * (Dias mes)) SI NO (Ingreso anual)")

    dias_bimestre = fields.Integer('No. dias bimestre')
    primer_mes_bimestre = fields.Float('Variable primer mes', 0.00)
    segundo_mes_bimestre = fields.Float('Variable segundo mes', 0.00)

    antiguedad = fields.Float('Antiguedad', 0.00, help="((Fecha de antiguedad) - (Fecha de hoy)) / 365")
    dias_de_vacaciones = fields.Integer('Dias de vacaciones',
                                        help="Dependiendo la antiguedad se busca en el rango de la tabla de vacaciones")
    aguinaldo = fields.Float('Aguinaldo', 0.00, help="(Salario diario * 30) / 365")
    prima_vacacional = fields.Float('Prima Vacacional', 0.00,
                                    help="(Dias de vacaciones * Salario diario * Prima vacacional(%)) / 365")
    despensa_en_efectivo = fields.Float('Despensa en efectivo', 0.00)
    dias = fields.Float('Dias Bimestre', 0.00,
                        help="(Variable primer mes del bimestre + Variable segundo mes del bimestre) / Numero dias bimestre")
    sdi = fields.Float('SDI', 0.00,
                       help="Salario diario + Aguinaldo + Prima vacacional + Despensa en efectivo + Dias bimestre")
    tope_salario = fields.Float('Tope salario', 0.00)
    tope_exento = fields.Float('Tope exento', 0.00, help="UMA * 0.4 * 30")
    exedente = fields.Float('Integra exedente', 0.00)

    fecha_ultima_actualizacion = fields.Datetime(string=_('Ultima Actualización'),
                                                 help="Fecha y hora de ultima actualización de los calculos")
    
    def calculo_sdi(self):
        ids_contratos = request.env['hr.contract'].search([('state', '=', 'open')]).ids

        for id in ids_contratos:

            contract = request.env['hr.contract'].search([('id', '=', id)])

            if contract.wage > 0:

                ingreso_anual = contract.wage * 12
                salario_diario = contract.wage / 30
                id_calculo_nomina = contract.tabla_nomina.id

                tabla_uma = request.env['tabla.nomina'].search([('id', '=', id_calculo_nomina)], limit=1)
                uma_actual = tabla_uma.uma
                porcentaje_pv = tabla_uma.porcentaje_prima_vacacional / 100
                periodo_mensual_en_dias = tabla_uma.periodo_mensual_en_dias
                uma_mensual = uma_actual * periodo_mensual_en_dias

                if contract.wage * 0.12 > uma_mensual:
                    ingreso_variable_mensual = uma_mensual
                else:
                    ingreso_variable_mensual = contract.wage * 0.12

                dif_dates = date.today() - contract.fecha_antiguedad
                antiguedad = dif_dates.days / 365

                dias = request.env['tabla.vacaciones'].search([('form_id', '=', tabla_uma.id),
                                                               ('antiguedad_minima', '<=', antiguedad),
                                                               ('antiguedad_maxima', '>=', antiguedad)])

                dias_de_vacaciones = dias.dias_vacaciones
                aguinaldo = (contract.salario_diario * 30) / 365

                prima_vacacional = (dias_de_vacaciones * salario_diario * porcentaje_pv) / 365

                despensa_en_efectivo = ingreso_variable_mensual / (periodo_mensual_en_dias + 0.02)

                # Dias del bimestre

                numero_dias_mes_actual_array = calendar.monthrange(date.today().year, date.today().month)
                numero_dias_mes_anterior_array = calendar.monthrange(date.today().year, date.today().month - 1)

                numero_dias_mes_actual = numero_dias_mes_actual_array[1]
                numero_dias_mes_anterior = numero_dias_mes_anterior_array[1]
                total_dias_meses = numero_dias_mes_actual + numero_dias_mes_anterior
                dias = (contract.primer_mes_bimestre + contract.segundo_mes_bimestre) / total_dias_meses

                # SDI
                sdi = salario_diario + aguinaldo + prima_vacacional + despensa_en_efectivo + dias

                # Tope de salario
                if sdi > 25 * uma_actual:
                    tope_de_salario = 25 * uma_actual
                else:
                    tope_de_salario = sdi

                # Tope exento
                tope_exento = uma_actual * 0.4 * 30

                # Exedente
                if tope_exento < ingreso_variable_mensual:
                    exedente = ingreso_variable_mensual - tope_exento
                else:
                    exedente = 0

                contract.write({'ingreso_anual': ingreso_anual,
                                'salario_diario': salario_diario,
                                'ingreso_variable_mensual': ingreso_variable_mensual,
                                'antiguedad': antiguedad,
                                'dias_de_vacaciones': dias_de_vacaciones,
                                'aguinaldo': aguinaldo,
                                'prima_vacacional': prima_vacacional,
                                'despensa_en_efectivo': despensa_en_efectivo,
                                'dias_bimestre': total_dias_meses,
                                'dias': dias,
                                'sdi': sdi,
                                'tope_salario': tope_de_salario,
                                'tope_exento': tope_exento,
                                'exedente': exedente,
                                'fecha_ultima_actualizacion': datetime.today()})
    
    # ACCION PARA GENERAR CALCULOS EN EL CONTRATO DEL TRABAJADOR POR MEDIO DEL BOTON

    def calculo_sdi_temp(self):
        if self.wage > 0:

            ingreso_anual = self.wage * 12
            salario_diario = self.wage / 30
            id_calculo_nomina = self.tabla_nomina.id

            tabla_uma = request.env['tabla.nomina'].search([('id', '=', id_calculo_nomina)], limit=1)
            uma_actual = tabla_uma.uma
            porcentaje_pv = tabla_uma.porcentaje_prima_vacacional / 100
            periodo_mensual_en_dias = tabla_uma.periodo_mensual_en_dias
            uma_mensual = uma_actual * periodo_mensual_en_dias

            if self.wage * 0.12 > uma_mensual:
                ingreso_variable_mensual = uma_mensual
            else:
                ingreso_variable_mensual = self.wage * 0.12

            dif_dates = date.today() - self.fecha_antiguedad
            antiguedad = dif_dates.days / 365

            dias = request.env['tabla.vacaciones'].search([('form_id', '=', tabla_uma.id),
                                                           ('antiguedad_minima', '<=', antiguedad),
                                                           ('antiguedad_maxima', '>=', antiguedad)])

            dias_de_vacaciones = dias.dias_vacaciones
            aguinaldo = (self.salario_diario * 30) / 365

            prima_vacacional = (dias_de_vacaciones * salario_diario * porcentaje_pv) / 365

            despensa_en_efectivo = ingreso_variable_mensual / (periodo_mensual_en_dias + 0.02)

            # Dias del bimestre

            numero_dias_mes_actual_array = calendar.monthrange(date.today().year, date.today().month)
            numero_dias_mes_anterior_array = calendar.monthrange(date.today().year, date.today().month - 1)

            numero_dias_mes_actual = numero_dias_mes_actual_array[1]
            numero_dias_mes_anterior = numero_dias_mes_anterior_array[1]
            total_dias_meses = numero_dias_mes_actual + numero_dias_mes_anterior
            dias = (self.primer_mes_bimestre + self.segundo_mes_bimestre) / total_dias_meses

            # SDI
            sdi = salario_diario + aguinaldo + prima_vacacional + despensa_en_efectivo + dias

            # Tope de salario
            if sdi > 25 * uma_actual:
                tope_de_salario = 25 * uma_actual
            else:
                tope_de_salario = sdi

            # Tope exento
            tope_exento = uma_actual * 0.4 * 30

            # Exedente
            if tope_exento < ingreso_variable_mensual:
                exedente = ingreso_variable_mensual - tope_exento
            else:
                exedente = 0

            self.ingreso_anual = ingreso_anual
            self.salario_diario = salario_diario
            self.ingreso_variable_mensual = ingreso_variable_mensual
            self.antiguedad = antiguedad
            self.dias_de_vacaciones = dias_de_vacaciones
            self.aguinaldo = aguinaldo
            self.prima_vacacional = prima_vacacional
            self.despensa_en_efectivo = despensa_en_efectivo
            self.dias_bimestre = total_dias_meses
            self.dias = dias
            self.sdi = sdi
            self.tope_salario = tope_de_salario
            self.tope_exento = tope_exento
            self.exedente = exedente
            self.fecha_ultima_actualizacion = datetime.today()


class TablaVacaciones(models.Model):
    _name = 'tabla.vacaciones'
    _description = "Tabla Vacaciones"

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


class CalculosNomina(models.Model):
    _inherit = "hr.payslip"

    # CAMPOS ISR

    tabla_nomina = fields.Many2one('tabla.nomina', 'Tabla nomina',
                                   help="Tabla de configuraciones con la cual se realizaran los calulos")
    ingreso_quincenal = fields.Float('Ingreso quincenal', 0.00)
    despensa_en_efectivo = fields.Float('Despensa en efectivo', 0.00)

    base_gravable = fields.Float('Base gravable', 0.00)
    limite_inferior = fields.Float('Limite inferior', 0.00)
    exedente_limite_inferior = fields.Float('Excedente del límite inferior', 0.00)
    porcentaje_exedente_limite_inferior = fields.Float('Excedente aplicable %', 0.00)
    impuesto_marginal = fields.Float('Impuesto marginal', 0.00)
    cuota_fija = fields.Float('Cuota fija', 0.00)
    impuesto_articulo_113 = fields.Float('Impuesto articulo 113', 0.00)
    subsidio_al_empleo = fields.Float('Subsidio del empleado', 0.00)
    isr_mensual = fields.Float('ISR Mensual', 0.00)
    isr_retenido = fields.Float('ISR Retenido', 0.00)

    # CAMPOS IMSS.
    tope_salario = fields.Float('Tope salario', 0.00)
    dias_de_cotizacion = fields.Float('Dias cotización', 0.00)
    dias_incapacidad = fields.Float('Dias incapacidad', 0.00)
    dias_ausencia = fields.Float('Dias ausencia', 0.00)

    # PRESTACIONES EN ESPECIE.
    pe_fija_patron = fields.Float('Fija Patron', 0.00)
    pe_smg_trabajador = fields.Float('Trabajador', 0.00)
    pe_smg_patron = fields.Float('Patron', 0.00)
    pe_smg_total = fields.Float('Total', 0.00, readonly=True)

    # PRESTACIONES EN DINERO.
    pd_unica_trabajador = fields.Float('Trabajador', 0.00)
    pd_unica_patron = fields.Float('Patron', 0.00)
    pd_unica_total = fields.Float('Total', 0.00, readonly=True)

    # GASTOS MEDICOS PENSIONADOS
    gmp_trabajador = fields.Float('Trabajador', 0.00)
    gmp_patron = fields.Float('Patron', 0.00)
    gmp_total = fields.Float('Total', 0.00, readonly=True)

    rt = fields.Float('RT', 0.00)

    # INVALIDEZ Y VIDA.
    iv_trabajador = fields.Float('Trabajador', 0.00)
    iv_patron = fields.Float('Patron', 0.00)
    iv_total = fields.Float('Total', 0.00, readonly=True)

    # GUARDERIAS Y PRESTACIONES SOCIALES.
    gps_trabajador = fields.Float('Trabajador', 0.00)
    gps_patron = fields.Float('Patron', 0.00)
    gps_total = fields.Float('Total', 0.00, readonly=True)

    # CUOTA MENSUAL
    cm_trabajador = fields.Float('Trabajador', 0.00)
    cm_patron = fields.Float('Patron', 0.00)
    cm_total = fields.Float('Total', 0.00, readonly=True)

    # CESANTIA Y VEJEZ.
    cv_trabajador = fields.Float('Trabajador', 0.00)
    cv_patron = fields.Float('Patron', 0.00)
    cv_total = fields.Float('Total', 0.00, readonly=True)

    # RETIRO.
    retiro_trabajador = fields.Float('Trabajador', 0.00)
    retiro_patron = fields.Float('Patron', 0.00)
    retiro_total = fields.Float('Total', 0.00, readonly=True)

    # TOTAL RCV
    total_rcv_trabajador = fields.Float('Trabajador', 0.00)
    total_rcv_patron = fields.Float('Patron', 0.00)
    total_rcv_total = fields.Float('Total', 0.00, readonly=True)

    # TOTAL INFONAVIT.
    total_infonavit_trabajador = fields.Float('Trabajador', 0.00)
    total_infonavit_patron = fields.Float('Patron', 0.00)
    total_infonavit_total = fields.Float('Total', 0.00, readonly=True)

    total_retencion_trabajador = fields.Float('Total retención', 0.00, readonly=True)

    def _calculo_isr(self, wage, id_tabla_nomina, ingreso_variable_mensual):

        # VARIABLES
        tabla_calculos = request.env['tabla.nomina'].search([('id', '=', id_tabla_nomina.id)], limit=1)

        salario_diario = wage / 30

        ingreso_q1 = salario_diario * 15
        ingreso_q2 = salario_diario * 15

        despensa_en_efectivo_q1 = ingreso_variable_mensual / 2
        despensa_en_efectivo_q2 = ingreso_variable_mensual / 2

        base_gravable = ingreso_q1 + ingreso_q2 + despensa_en_efectivo_q1 + despensa_en_efectivo_q2

        isr_mensual = request.env['tabla.isr'].search([('form_id', '=', tabla_calculos.id),
                                                       ('limite_inferior', '<', base_gravable),
                                                       ('limite_superior', '>', base_gravable)])

        limite_inferior = isr_mensual.limite_inferior

        exedente_del_limite_inferior = base_gravable - limite_inferior

        porcentaje_limite_inferior = isr_mensual.exedente / 100

        impuesto_marginal = exedente_del_limite_inferior * porcentaje_limite_inferior

        cuota_fija = isr_mensual.cuota_fija

        impuesto_articulo_113 = impuesto_marginal + cuota_fija

        subsidio_del_empleado = request.env['tabla.subsidio.empleo'].search([('form_id', '=', tabla_calculos.id),
                                                                             ('limite_inferior', '<=',
                                                                              base_gravable),
                                                                             ('limite_superior', '>=',
                                                                              base_gravable)])

        subsidio_al_empleo = subsidio_del_empleado.credito

        isr_monto_mensual = impuesto_articulo_113 - subsidio_al_empleo

        isr_retencion_q1 = isr_monto_mensual / 2

        isr_retencion_q2 = isr_monto_mensual - isr_retencion_q1

        return isr_retencion_q1

    def _calculo_imss(self, id_tabla_nomina, tope_salario):
        
        calculos = request.env['tabla.nomina'].search([('id', '=', id_tabla_nomina.id)], limit=1)
        uma_actual = calculos.uma
        
        Total_retencion = 0

        if tope_salario > 0:
            PE_fija = (uma_actual * calculos.cuota_fija_trabajador / 100) * 15

            # PRESTACIONES EN ESPECIE (PE)
            if tope_salario > uma_actual * 3:
                PE_3SMG_trab = ((tope_salario - (uma_actual * 3)) * calculos.excedente_trabajador / 100) * 15
                PE_3SMG_patron = ((tope_salario - (uma_actual * 3)) * calculos.excedente_patron / 100) * 15
                PE_3SMG_total = PE_3SMG_trab + PE_3SMG_patron

            # PRESTACIONES EN DINERO (PD)
            PD_unica_trab = (tope_salario * 15) * (calculos.prestaciones_en_dinero_trabajador / 100)
            PD_unica_patron = (tope_salario * 15) * (calculos.prestaciones_en_dinero_patron / 100)
            PD_unica_total = PD_unica_trab + PD_unica_patron

            # GASTOS MEDICOS PENSIONADOS (GMP)
            GMP_trab = (tope_salario * 15) * (calculos.gastos_medicos_pensionados_trabajador / 100)
            GMP_patron = (tope_salario * 15) * (calculos.gastos_medicos_pensionados_patron / 100)
            GMP_total = GMP_trab + GMP_patron

            RT = (tope_salario * 15) * (calculos.porcentaje_prima_de_riesgo / 100)

            # INVALIDEZ Y VIDA (IV)

            if tope_salario < (calculos.limite_inv_y_vid_y_cv * calculos.salario_minimo_vigente):
                IV_trab = (tope_salario * 15) * (calculos.invalidez_y_vida_trabajador / 100)
                IV_patron = (tope_salario * 15) * (calculos.invalidez_y_vida_trabajador / 100)
            else:
                IV_trab = ((calculos.limite_inv_y_vid_y_cv * calculos.salario_minimo_vigente) * 15) * (
                            calculos.invalidez_y_vida_trabajador / 100)
                IV_patron = ((calculos.limite_inv_y_vid_y_cv * calculos.salario_minimo_vigente) * 15) * (
                            calculos.invalidez_y_vida_patron / 100)

            IV_total = IV_trab + IV_patron

            # GUARDERIAS Y PREST SOC (GPS)

            GSP_trab = (tope_salario * 15) * (calculos.guarderias_y_gastos_de_prevision_social_trabajador / 100)
            GSP_patron = (tope_salario * 15) * (calculos.guarderias_y_gastos_de_prevision_social_patron / 100)
            GSP_total = GSP_trab + GSP_patron

            cuota_mensual_trab = PE_3SMG_trab + PD_unica_trab + GMP_trab + IV_trab
            cuota_mensual_patron = PE_fija + PE_3SMG_patron + PD_unica_patron + RT + GMP_patron + IV_patron + GSP_patron
            cuota_mensual_total = cuota_mensual_trab + cuota_mensual_patron

            #  CESANTIA Y VEJEZ (CV)
            if tope_salario < (calculos.limite_inv_y_vid_y_cv * calculos.salario_minimo_vigente):
                cesantia_y_vejez_trab = (tope_salario * 15) * (calculos.cesantia_y_vejez_trabajador / 100)
                cesantia_y_vejez_patron = (tope_salario * 15) * (calculos.cesantia_y_vejez_patron / 100)
            else:
                cesantia_y_vejez_trab = ((calculos.limite_inv_y_vid_y_cv * calculos.salario_minimo_vigente) * 15) * (
                            calculos.cesantia_y_vejez_trabajador / 100)
                cesantia_y_vejez_patron = ((calculos.limite_inv_y_vid_y_cv * calculos.salario_minimo_vigente) * 15) * (
                            calculos.cesantia_y_vejez_patron / 100)

            cesantia_total = cesantia_y_vejez_trab + cesantia_y_vejez_patron

            # RETIRO

            retiro_trab = (tope_salario * 15) * (calculos.retiro_trabajador / 100)
            retiro_patron = (tope_salario * 15) * (calculos.retiro_patron / 100)
            retiro_total = retiro_trab + retiro_patron

            # TOTAL RCV (TRCV)
            TRCV_trab = cesantia_y_vejez_trab + retiro_trab
            TRCV_patron = cesantia_y_vejez_patron + retiro_patron
            TRCV_total = TRCV_trab + TRCV_patron

            # TOTAL INFONAVIT (TI)
            TI_trab = (tope_salario * 15) * calculos.infonavit_trabajador

            if tope_salario < (calculos.limite_inv_y_vid_y_cv * calculos.salario_minimo_vigente):
                TI_patron = (tope_salario * 15) * (calculos.infonavit_patron / 100)
            else:
                TI_patron = ((calculos.limite_inv_y_vid_y_cv * calculos.salario_minimo_vigente) * 15) * calculos.infonavit_patron

            TI_total = TI_trab + TI_patron

            Total_retencion = round(cuota_mensual_trab + TRCV_trab + TI_trab, 2)

        return Total_retencion

    def compute_sheet(self):

        for contract in self:

            if contract.contract_id.wage > 0 and contract.contract_id.tabla_nomina:

                # ISR
                tabla_calculos = request.env['tabla.nomina'].search([('id', '=', self.contract_id.tabla_nomina.id)],
                                                                    limit=1)
                salario_diario = contract.contract_id.wage / 30
                ingreso_q1 = salario_diario * 15
                ingreso_q2 = salario_diario * 15
                despensa_en_efectivo_q1 = contract.contract_id.ingreso_variable_mensual / 2
                despensa_en_efectivo_q2 = contract.contract_id.ingreso_variable_mensual / 2
                base_gravable = ingreso_q1 + ingreso_q2 + despensa_en_efectivo_q1 + despensa_en_efectivo_q2
                isr_mensual = request.env['tabla.isr'].search([('form_id', '=', tabla_calculos.id),
                                                               ('limite_inferior', '<', base_gravable),
                                                               ('limite_superior', '>', base_gravable)])

                limite_inferior = isr_mensual.limite_inferior
                exedente_del_limite_inferior = base_gravable - limite_inferior
                porcentaje_limite_inferior = isr_mensual.exedente / 100
                impuesto_marginal = exedente_del_limite_inferior * porcentaje_limite_inferior
                cuota_fija = isr_mensual.cuota_fija
                impuesto_articulo_113 = impuesto_marginal + cuota_fija
                subsidio_del_empleado = request.env['tabla.subsidio.empleo'].search(
                    [('form_id', '=', tabla_calculos.id),
                     ('limite_inferior', '<=',
                      base_gravable),
                     ('limite_superior', '>=',
                      base_gravable)])
                subsidio_al_empleo = subsidio_del_empleado.credito
                isr_monto_mensual = impuesto_articulo_113 - subsidio_al_empleo
                isr_retencion_q1 = isr_monto_mensual / 2
                isr_retencion_q2 = isr_monto_mensual - isr_retencion_q1

                # Calculos ISR
                self.ingreso_quincenal = ingreso_q1
                self.despensa_en_efectivo = despensa_en_efectivo_q1
                self.base_gravable = base_gravable
                self.limite_inferior = limite_inferior
                self.exedente_limite_inferior = exedente_del_limite_inferior
                self.porcentaje_exedente_limite_inferior = porcentaje_limite_inferior * 100
                self.impuesto_marginal = impuesto_marginal
                self.cuota_fija = cuota_fija
                self.impuesto_articulo_113 = impuesto_articulo_113
                self.subsidio_al_empleo = subsidio_al_empleo
                self.isr_mensual = isr_monto_mensual
                self.isr_retenido = isr_retencion_q1

                # ---------------------------------------------------------------------------------------------------
                # IMSS
                uma_actual = tabla_calculos.uma
                tope_salario = contract.contract_id.tope_salario

                if tope_salario > 0:
                    PE_fija = (uma_actual * tabla_calculos.cuota_fija_trabajador / 100) * 15

                    # PRESTACIONES EN ESPECIE (PE)
                    if tope_salario > uma_actual * 3:
                        PE_3SMG_trab = ((tope_salario - (
                                    uma_actual * 3)) * tabla_calculos.excedente_trabajador / 100) * 15
                        PE_3SMG_patron = ((tope_salario - (
                                    uma_actual * 3)) * tabla_calculos.excedente_patron / 100) * 15
                        PE_3SMG_total = PE_3SMG_trab + PE_3SMG_patron

                    # PRESTACIONES EN DINERO (PD)
                    PD_unica_trab = (tope_salario * 15) * (tabla_calculos.prestaciones_en_dinero_trabajador / 100)
                    PD_unica_patron = (tope_salario * 15) * (tabla_calculos.prestaciones_en_dinero_patron / 100)
                    PD_unica_total = PD_unica_trab + PD_unica_patron

                    # GASTOS MEDICOS PENSIONADOS (GMP)
                    GMP_trab = (tope_salario * 15) * (tabla_calculos.gastos_medicos_pensionados_trabajador / 100)
                    GMP_patron = (tope_salario * 15) * (tabla_calculos.gastos_medicos_pensionados_patron / 100)
                    GMP_total = GMP_trab + GMP_patron

                    RT = (tope_salario * 15) * (tabla_calculos.porcentaje_prima_de_riesgo / 100)

                    # INVALIDEZ Y VIDA (IV)

                    if tope_salario < (tabla_calculos.limite_inv_y_vid_y_cv * tabla_calculos.salario_minimo_vigente):
                        IV_trab = (tope_salario * 15) * (tabla_calculos.invalidez_y_vida_trabajador / 100)
                        IV_patron = (tope_salario * 15) * (tabla_calculos.invalidez_y_vida_trabajador / 100)
                    else:
                        IV_trab = ((
                                           tabla_calculos.limite_inv_y_vid_y_cv * tabla_calculos.salario_minimo_vigente) * 15) * (
                                          tabla_calculos.invalidez_y_vida_trabajador / 100)
                        IV_patron = ((
                                             tabla_calculos.limite_inv_y_vid_y_cv * tabla_calculos.salario_minimo_vigente) * 15) * (
                                            tabla_calculos.invalidez_y_vida_patron / 100)

                    IV_total = IV_trab + IV_patron

                    # GUARDERIAS Y PREST SOC (GPS)

                    GSP_trab = (tope_salario * 15) * (
                            tabla_calculos.guarderias_y_gastos_de_prevision_social_trabajador / 100)
                    GSP_patron = (tope_salario * 15) * (
                                tabla_calculos.guarderias_y_gastos_de_prevision_social_patron / 100)
                    GSP_total = GSP_trab + GSP_patron

                    cuota_mensual_trab = PE_3SMG_trab + PD_unica_trab + GMP_trab + IV_trab
                    cuota_mensual_patron = PE_fija + PE_3SMG_patron + PD_unica_patron + RT + GMP_patron + IV_patron + GSP_patron
                    cuota_mensual_total = cuota_mensual_trab + cuota_mensual_patron

                    #  CESANTIA Y VEJEZ (CV)
                    if tope_salario < (tabla_calculos.limite_inv_y_vid_y_cv * tabla_calculos.salario_minimo_vigente):
                        cesantia_y_vejez_trab = (tope_salario * 15) * (tabla_calculos.cesantia_y_vejez_trabajador / 100)
                        cesantia_y_vejez_patron = (tope_salario * 15) * (tabla_calculos.cesantia_y_vejez_patron / 100)
                    else:
                        cesantia_y_vejez_trab = ((
                                                         tabla_calculos.limite_inv_y_vid_y_cv * tabla_calculos.salario_minimo_vigente) * 15) * (
                                                        tabla_calculos.cesantia_y_vejez_trabajador / 100)
                        cesantia_y_vejez_patron = ((
                                                           tabla_calculos.limite_inv_y_vid_y_cv * tabla_calculos.salario_minimo_vigente) * 15) * (
                                                          tabla_calculos.cesantia_y_vejez_patron / 100)

                    cesantia_total = cesantia_y_vejez_trab + cesantia_y_vejez_patron

                    # RETIRO

                    retiro_trab = (tope_salario * 15) * (tabla_calculos.retiro_trabajador / 100)
                    retiro_patron = (tope_salario * 15) * (tabla_calculos.retiro_patron / 100)
                    retiro_total = retiro_trab + retiro_patron

                    # TOTAL RCV (TRCV)
                    TRCV_trab = cesantia_y_vejez_trab + retiro_trab
                    TRCV_patron = cesantia_y_vejez_patron + retiro_patron
                    TRCV_total = TRCV_trab + TRCV_patron

                    # TOTAL INFONAVIT (TI)
                    TI_trab = (tope_salario * 15) * (tabla_calculos.infonavit_trabajador / 100)

                    if tope_salario < (tabla_calculos.limite_inv_y_vid_y_cv * tabla_calculos.salario_minimo_vigente):
                        TI_patron = (tope_salario * 15) * (tabla_calculos.infonavit_patron / 100)
                    else:
                        TI_patron = ((
                                             tabla_calculos.limite_inv_y_vid_y_cv * tabla_calculos.salario_minimo_vigente) * 15) * (
                                            tabla_calculos.infonavit_patron / 100)

                    TI_total = TI_trab + TI_patron

                    Total_retencion = round(cuota_mensual_trab + TRCV_trab + TI_trab, 2)

                    # CAMPOS IMSS
                    self.tope_salario = tope_salario
                    self.dias_de_cotizacion = 15
                    self.dias_incapacidad = 0
                    self.dias_ausencia = 0

                    # PRESTACIONES EN ESPECIE
                    self.pe_fija_patron = PE_fija
                    self.pe_smg_trabajador = PE_3SMG_trab
                    self.pe_smg_patron = PE_3SMG_patron
                    self.pe_smg_total = PE_3SMG_total

                    # PRESTACIONES EN DINERO
                    self.pd_unica_trabajador = PD_unica_trab
                    self.pd_unica_patron = PD_unica_patron
                    self.pd_unica_total = PD_unica_total

                    # GASTOS MEDICOS PENSIONADOS
                    self.gmp_trabajador = GMP_trab
                    self.gmp_patron = GMP_patron
                    self.gmp_total = GMP_total

                    self.rt = RT

                    # INVALIDEZ Y VIDA
                    self.iv_trabajador = IV_trab
                    self.iv_patron = IV_patron
                    self.iv_total = IV_total

                    # GUARDERIAS Y PRESTACIONES SOCIALES
                    self.gps_trabajador = GSP_trab
                    self.gps_patron = GSP_patron
                    self.gps_total = GSP_total

                    # CUOTA MENSUAL
                    self.cm_trabajador = cuota_mensual_trab
                    self.cm_patron = cuota_mensual_patron
                    self.cm_total = cuota_mensual_total

                    # CESANTIA Y VEJEZ
                    self.cv_trabajador = cesantia_y_vejez_trab
                    self.cv_patron = cesantia_y_vejez_patron
                    self.cv_total = cesantia_total

                    # RETIRO
                    self.retiro_trabajador = retiro_trab
                    self.retiro_patron = retiro_patron
                    self.retiro_total = retiro_total

                    # TOTAL RCV
                    self.total_rcv_trabajador = TRCV_trab
                    self.total_rcv_patron = TRCV_patron
                    self.total_rcv_total = TRCV_total

                    # INFONAVIT
                    self.total_infonavit_trabajador = TI_trab
                    self.total_infonavit_patron = TI_patron
                    self.total_infonavit_total = TI_total

                    self.total_retencion_trabajador = Total_retencion

                res = super(CalculosNomina, self).compute_sheet()
                return res
        

class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def compute_sheet(self):
        self.ensure_one()
        if not self.env.context.get('active_id'):
            from_date = fields.Date.to_date(self.env.context.get('default_date_start'))
            end_date = fields.Date.to_date(self.env.context.get('default_date_end'))
            payslip_run = self.env['hr.payslip.run'].create({
                'name': from_date.strftime('%B %Y'),
                'date_start': from_date,
                'date_end': end_date,
            })
        else:
            payslip_run = self.env['hr.payslip.run'].browse(self.env.context.get('active_id'))

        if not self.employee_ids:
            raise UserError(_("You must select employee(s) to generate payslip(s)."))

        payslips = self.env['hr.payslip']
        Payslip = self.env['hr.payslip']

        contracts = self.employee_ids._get_contracts(payslip_run.date_start, payslip_run.date_end,
                                                     states=['open', 'close'])
        contracts._generate_work_entries(payslip_run.date_start, payslip_run.date_end)
        work_entries = self.env['hr.work.entry'].search([
            ('date_start', '<=', payslip_run.date_end),
            ('date_stop', '>=', payslip_run.date_start),
            ('employee_id', 'in', self.employee_ids.ids),
        ])
        self._check_undefined_slots(work_entries, payslip_run)

        validated = work_entries.action_validate()
        if not validated:
            raise UserError(_("Some work entries could not be validated."))

        default_values = Payslip.default_get(Payslip.fields_get())
        for contract in contracts:
            values = dict(default_values, **{
                'employee_id': contract.employee_id.id,
                'credit_note': payslip_run.credit_note,
                'payslip_run_id': payslip_run.id,
                'date_from': payslip_run.date_start,
                'date_to': payslip_run.date_end,
                'contract_id': contract.id,
                'struct_id': self.structure_id.id or contract.structure_type_id.default_struct_id.id,
            })
            payslip = self.env['hr.payslip'].new(values)
            payslip._onchange_employee()
            values = payslip._convert_to_write(payslip._cache)
            payslips += Payslip.create(values)
        payslips.compute_sheet()
        payslip_run.state = 'verify'

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.payslip.run',
            'views': [[False, 'form']],
            'res_id': payslip_run.id,
        }
