from odoo import models, api, _, fields
from datetime import datetime, date
import calendar
from odoo.http import request


class HrContract(models.Model):
    _inherit = "hr.contract"

    # NUEVOS CAMPOS EN MODULO DE CONTRATOS
    
    # CAMPOS DE BAJA DE EMPLEADO    
    departure_reason = fields.Selection(
        selection=[('voluntario', 'Voluntario'),
                   ('involuntario', 'Involuntario'),
                   ('retiro', 'Retiro'), ],
        string=_('Razón de salida'))
    departure_description = fields.Text('Motivo de salida')

    # CAMPOS DE ENTRADA PARA CALCULOS DE SDI Y NOMINA
    tabla_nomina = fields.Many2one('tabla.nomina', 'Tabla nomina',
                                   help="Tabla de configuraciones con la cual se realizaran los calulos")
    fecha_antiguedad = fields.Date(string=_('Fecha de antiguedad'), help="Fecha utilizada para generar calculos")
    fecha_antiguedad_imss = fields.Date(string=_('Fecha de antiguedad en el IMSS'), help="Fecha utilizada para generar calculos")

    # CAMPOS DE SOLO LECTURA PARA EFECTOS DE CALCULOS SDI Y NOMINA
    ingreso_anual = fields.Float('Ingreso anual', 0.00, help="(Ingreso mensual) * 12")
    salario_diario = fields.Float('Salario diario', 0.00, help="(Ingreso mensual) / 30")
    ingreso_variable_mensual = fields.Float('Ingreso variable mensual', 0.00,
                                            help="SI (Ingreso anual > ((UMA) * (Dias mes)) ENTONCES ((UMA) * (Dias mes)) SI NO (Ingreso anual)")

    dias_bimestre = fields.Integer('No. dias del bimestre')
    primer_mes_bimestre = fields.Float('Variable de primas de primer mes del bimestre anterior', 0.00)
    segundo_mes_bimestre = fields.Float('Variable de primas del segundo mes del bimestre anterior', 0.00)

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

    # CALCULOS DE SDI
    def calculo_sdi_automata(self):
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

                despensa_en_efectivo = ingreso_variable_mensual / (periodo_mensual_en_dias)

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
    def calculo_sdi_manual(self):
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

            despensa_en_efectivo = ingreso_variable_mensual / (periodo_mensual_en_dias)

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