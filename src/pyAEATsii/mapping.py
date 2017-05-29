
__all__ = [
    'get_headers',
    'build_query_filter',
    'IssuedInvoiceMapper',
    'RecievedInvoiceMapper',
    'hardcode',
]

from sets import ImmutableSet

_DATE_FMT = '%d-%m-%Y'
RECTIFIED_KINDS = ImmutableSet({'R1', 'R2', 'R3', 'R4', 'R5'})


def _format_period(period):
    return str(period).zfill(2)


def build_query_filter(year=None, period=None):
    return {
        'PeriodoImpositivo': {
            'Ejercicio': year,
            'Periodo': _format_period(period),
        }
        # TODO: IDFactura, Contraparte,
        # FechaPresentacion, FacturaModificada,
        # EstadoCuadre, ClavePaginacion
    }


def get_headers(name=None, vat=None, comm_kind=None, version='0.7'):
    return {
        'IDVersionSii': version,
        'Titular': {
            'NombreRazon': name,
            'NIF': vat,
            # TODO: NIFRepresentante
        },
        'TipoComunicacion': comm_kind,
    }


class _HardcodedValue(object):

    def __init__(self, value):
        self.value = value

    def __call__(self, *args, **kwargs):
        return self.value


def hardcode(value):
    return _HardcodedValue(value)


class IssuedInvoiceMapper(object):

    @classmethod
    def build_delete_request(cls, invoice):
        return {
            'PeriodoImpositivo': cls.build_period(invoice),
            'IDFactura': cls.build_invoice_id(invoice),
        }

    @classmethod
    def build_submit_request(cls, invoice):
        request = cls.build_delete_request(invoice)
        request['FacturaExpedida'] = cls.build_issued_invoice(invoice)
        return request

    @classmethod
    def build_period(cls, invoice):
        return {
            'Ejercicio': cls.year(invoice),
            'Periodo': _format_period(cls.period(invoice)),
        }

    @classmethod
    def build_invoice_id(cls, invoice):
        return {
            'IDEmisorFactura': {
                'NIF': cls.nif(invoice),
            },
            'NumSerieFacturaEmisor': cls.serial_number(invoice),
            # TODO: NumSerieFacturaEmisorResumenFinal
            'FechaExpedicionFacturaEmisor':
                cls.issue_date(invoice).strftime(_DATE_FMT),
        }

    @classmethod
    def build_issued_invoice(cls, invoice):
        ret = {
            'TipoFactura': cls.invoice_kind(invoice),
            # TODO: FacturasAgrupadas
            # TODO: FacturasRectificadas
            # TODO: FechaOperacion
            'ClaveRegimenEspecialOTrascendencia':
                cls.specialkey_or_trascendence(invoice),
            # TODO: ClaveRegimenEspecialOTrascendenciaAdicional1
            # TODO: ClaveRegimenEspecialOTrascendenciaAdicional2
            # TODO: NumRegistroAcuerdoFacturacion
            # TODO: ImporteTotal
            # TODO: BaseImponibleACoste
            'DescripcionOperacion': cls.description(invoice),
            # TODO: DatosInmueble
            # TODO: ImporteTransmisionSujetoAIVA
            # TODO: EmitidaPorTerceros
            # TODO: VariosDestinatarios
            # TODO: Cupon
            'TipoDesglose': {
                'DesgloseFactura': {
                    'Sujeta': {
                        # 'Exenta': {
                        #     'CausaExcencion': E1-E6
                        #     'BaseImponible': '0.00',
                        # },
                        'NoExenta': {
                            'TipoNoExenta': cls.not_exempt_kind(invoice),
                            'DesgloseIVA': {
                                'DetalleIVA':
                                    map(cls.build_taxes, cls.taxes(invoice)),
                            }
                        },
                    },
                    # 'NoSujeta': {
                    #     'ImportePorArticulos7_14_Otros': 0,
                    #     'ImporteTAIReglasLocalizacion': 0,
                    # },
                },
                # 'DesgloseTipoOperacion': {
                #     'PrestacionDeServicios':
                #         {'Sujeta': {'Exenta': {}, 'NoExenta': {}}, 'NoSujeta': {}},
                #     'Entrega':
                #         {'Sujeta': {'Exenta': {}, 'NoExenta': {}}, 'NoSujeta': {}},
                # },
            },
        }
        cls._update_total_amount(ret, invoice)
        cls._update_counterpart(ret, invoice)
        cls._update_rectified_invoice(ret, invoice)
        return ret

    @classmethod
    def _update_total_amount(cls, ret, invoice):
        if (
            ret['TipoFactura'] == 'R5' and
            len(
                ret['TipoDesglose']['DesgloseFactura']['Sujeta']['NoExenta']
                ['DesgloseIVA']['DetalleIVA']
            ) == 1 and
            (
                ret['TipoDesglose']['DesgloseFactura']['Sujeta']['NoExenta']
                ['DesgloseIVA']['DetalleIVA'][0]['BaseImponible'] == 0
            )
        ):
            ret['ImporteTotal'] = cls.total_amount(invoice)

    @classmethod
    def _update_counterpart(cls, ret, invoice):
        if ret['TipoFactura'] not in {'F2', 'F4', 'R5'}:
            ret['Contraparte'] = cls.build_counterpart(invoice)

    @classmethod
    def _update_rectified_invoice(cls, ret, invoice):
        if ret['TipoFactura'] in RECTIFIED_KINDS:
            ret['TipoRectificativa'] = cls.rectified_invoice_kind(invoice)
            if ret['TipoRectificativa'] == 'S':
                ret['ImporteRectificacion'] = {
                    'BaseRectificada': cls.rectified_base(invoice),
                    'CuotaRectificada': cls.rectified_amount(invoice),
                    # TODO: CuotaRecargoRectificado
                }

    @classmethod
    def build_counterpart(cls, invoice):
        return {
            'NombreRazon': cls.counterpart_name(invoice),
            'NIF': cls.counterpart_nif(invoice),
            # 'IDOtro': {
            #     'IDType': cls.counterpart_id_type(invoice),
            #     'CodigoPais': cls.counterpart_country(invoice),
            #     'ID': cls.counterpart_nif(invoice),
            # },
        }

    @classmethod
    def build_taxes(cls, tax):
        return {
            'TipoImpositivo': int(100 * cls.tax_rate(tax)),
            'BaseImponible': cls.tax_base(tax),
            'CuotaRepercutida': cls.tax_amount(tax),
            # TODO: TipoRecargoEquivalencia, CuotaRecargoEquivalencia
        }


class RecievedInvoiceMapper(object):

    @classmethod
    def build_delete_request(cls, invoice):
        return {
            'PeriodoImpositivo': cls.build_period(invoice),
            'IDFactura': cls.build_named_invoice_id(invoice),
        }

    @classmethod
    def build_submit_request(cls, invoice):
        return {
            'PeriodoImpositivo': cls.build_period(invoice),
            'IDFactura': cls.build_invoice_id(invoice),
            'FacturaRecibida': cls.build_invoice(invoice),
        }

    @classmethod
    def build_period(cls, invoice):
        return {
            'Ejercicio': cls.year(invoice),
            'Periodo': _format_period(cls.period(invoice)),
        }

    @classmethod
    def build_invoice_id(cls, invoice):
        return {
            'IDEmisorFactura': {
                'NIF': cls.counterpart_nif(invoice),
                # TODO: IDOtro: {CodigoPais, IDType, ID}
            },
            'NumSerieFacturaEmisor': cls.serial_number(invoice),
            # TODO: NumSerieFacturaEmisorResumenFin
            'FechaExpedicionFacturaEmisor':
                cls.issue_date(invoice).strftime(_DATE_FMT),
        }

    @classmethod
    def build_named_invoice_id(cls, invoice):
        return {
            'IDEmisorFactura': {
                'NombreRazon': cls.counterpart_name(invoice),
                'NIF': cls.counterpart_nif(invoice),
            },
            'NumSerieFacturaEmisor': cls.serial_number(invoice),
            'FechaExpedicionFacturaEmisor':
                cls.issue_date(invoice).strftime(_DATE_FMT),
        }

    @classmethod
    def build_invoice(cls, invoice):
        ret = {
            'TipoFactura': cls.invoice_kind(invoice),
            # TODO: FacturasAgrupadas: {IDFacturaAgrupada: [{Num, Fecha}]}
            # TODO: FechaOperacion
            'ClaveRegimenEspecialOTrascendencia':
                cls.specialkey_or_trascendence(invoice),
            # TODO: ClaveRegimenEspecialOTrascendenciaAdicional1
            # TODO: ClaveRegimenEspecialOTrascendenciaAdicional2
            # TODO: NumRegistroAcuerdoFacturacion
            # TODO: ImporteTotal
            # TODO: BaseImponibleACoste
            'DescripcionOperacion': cls.description(invoice),
            'DesgloseFactura': {
                # 'InversionSujetoPasivo': {
                #     'DetalleIVA':
                #         map(cls.build_taxes, cls.taxes(invoice)),
                # },
                'DesgloseIVA': {
                    'DetalleIVA':
                        map(cls.build_taxes, cls.taxes(invoice)),
                }
            },
            'Contraparte': cls.build_counterpart(invoice),
            'FechaRegContable': cls.move_date(invoice).strftime(_DATE_FMT),
            'CuotaDeducible': cls.deductible_amount(invoice),
        }
        cls._update_rectified_invoice(ret, invoice)
        return ret

    @classmethod
    def _update_rectified_invoice(cls, ret, invoice):
        if ret['TipoFactura'] in RECTIFIED_KINDS:
            ret['TipoRectificativa'] = cls.rectified_invoice_kind(invoice)
            # TODO: FacturasRectificadas:{IDFacturaRectificada:[{Num, Fecha}]}
            # TODO: ImporteRectificacion: {
            #   BaseRectificada, CuotaRectificada, CuotaRecargoRectificado }

    @classmethod
    def build_counterpart(cls, invoice):
        return {
            'NombreRazon': cls.counterpart_name(invoice),
            'NIF': cls.counterpart_nif(invoice),
            # 'IDOtro': {
            #     'IDType': cls.counterpart_id_type(invoice),
            #     'CodigoPais': cls.counterpart_country(invoice),
            #     # 'ID': cls.counterpart_nif(invoice),
            # },
        }

    @classmethod
    def build_taxes(cls, tax):
        return {
            'TipoImpositivo': int(100 * cls.tax_rate(tax)),
            'BaseImponible': cls.tax_base(tax),
            'CuotaSoportada': cls.tax_amount(tax),
            # TODO: TipoRecargoEquivalencia, CuotaRecargoEquivalencia
            # TODO: PorcentCompensacionREAGYP, ImporteCompensacionREAGYP
        }
