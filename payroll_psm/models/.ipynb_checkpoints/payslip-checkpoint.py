from odoo import models, api, _, fields
from odoo.http import request
from odoo.exceptions import AccessError, UserError, RedirectWarning, ValidationError, Warning
from datetime import datetime, date
from datetime import timedelta
import calendar


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
                TI_patron = ((
                                         calculos.limite_inv_y_vid_y_cv * calculos.salario_minimo_vigente) * 15) * calculos.infonavit_patron

            TI_total = TI_trab + TI_patron

            Total_retencion = round(cuota_mensual_trab + TRCV_trab + TI_trab, 2)

        return Total_retencion
    
    def _calculo_pv(self, id_tabla_nomina, salario_diario, dias_de_vacaciones, fecha_antiguedad, fecha_pago_nomina):

        tabla_calculos = request.env['tabla.nomina'].search([('id', '=', id_tabla_nomina.id)], limit=1)
        porcentaje_prima_vacacional = tabla_calculos.porcentaje_prima_vacacional / 100
        anio_antiguedad = fecha_antiguedad.year
        anio_actual = datetime.today().year

        # Variable global
        prima_vacacional = 0

        if anio_antiguedad < anio_actual:
            dia_fecha_pago_nomina = fecha_pago_nomina.day
            fecha_pago_pv_actual = fecha_antiguedad.replace(year=anio_actual)

            if dia_fecha_pago_nomina == 15:

                ultimo_dia_mes = self.ultimo_dia_del_mes(fecha_pago_nomina)

                if fecha_pago_nomina < fecha_pago_pv_actual <= ultimo_dia_mes or fecha_pago_pv_actual == fecha_pago_nomina:
                    prima_vacacional = (salario_diario * dias_de_vacaciones) * porcentaje_prima_vacacional
                else:
                    prima_vacacional = 0

            elif dia_fecha_pago_nomina == 28 or 29 or 30 or 31:

                siguiente_quincena = fecha_pago_nomina + timedelta(days=15)
                fecha_pago = siguiente_quincena.replace(day=15)

                if fecha_pago_nomina < fecha_pago_pv_actual <= siguiente_quincena or fecha_pago_pv_actual == fecha_pago_nomina:
                    prima_vacacional = (salario_diario * dias_de_vacaciones) * porcentaje_prima_vacacional
                else:
                    prima_vacacional = 0

        return prima_vacacional

    def ultimo_dia_del_mes(self, fecha):
        return fecha.replace(day=calendar.monthrange(fecha.year, fecha.month)[1])

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
    
    def condicional_prima_vacacional(self):

        fecha_antiguedad = self.fecha_antiguedad
        fecha_actual = datetime.today()

        year_antiguedad = fecha_antiguedad.year
        year_actual = fecha_actual.year

        # Condicional para detectar si ya tiene mas de un año de antiguedad
        if year_antiguedad < year_actual:

            fecha_pago_nomina_texto = '09-15-2020'
            fecha_pago_nomina = datetime.strptime(fecha_pago_nomina_texto, '%m-%d-%Y').date()

            fecha_antiguedad_actual = fecha_antiguedad.replace(year=year_actual)

            ultimo_dia_mes = self.ultimo_dia_del_mes(fecha_antiguedad_actual)

            dia_quince_mes_actual = ultimo_dia_mes.replace(day=15)

            if fecha_pago_nomina < fecha_antiguedad_actual <= ultimo_dia_mes or fecha_antiguedad_actual == dia_quince_mes_actual:
                print("Si aplica para pv")
            else:
                print("No aplica")