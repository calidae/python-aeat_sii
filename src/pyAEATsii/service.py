
__all__ = [
    'bind_issued_invoices_service',
    'bind_recieved_invoices_service',
]

from logging import getLogger
from requests import Session

from zeep import Client
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin

from .plugins import LoggingPlugin
from .mapping import build_query_filter

_logger = getLogger(__name__)


def _get_client(wsdl, public_crt, private_key, test=False):
    session = Session()
    session.cert = (public_crt, private_key)
    transport = Transport(session=session)
    plugins = [HistoryPlugin()]
    # TODO: manually handle sessionId? Not mandatory yet recommended...
    # http://www.agenciatributaria.es/AEAT.internet/Inicio/Ayuda/Modelos__Procedimientos_y_Servicios/Ayuda_P_G417____IVA__Llevanza_de_libros_registro__SII_/Ayuda_tecnica/Informacion_tecnica_SII/Preguntas_tecnicas_frecuentes/1__Cuestiones_Generales/16___Como_se_debe_utilizar_el_dato_sesionId__.shtml
    if test:
        plugins.append(LoggingPlugin())
    client = Client(wsdl=wsdl, transport=transport, plugins=plugins)
    return client


def bind_issued_invoices_service(crt, pkey, test=False):
    wsdl = (
        'http://www.agenciatributaria.es/static_files/AEAT/'
        'Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/'
        'Suministro_inmediato_informacion/FicherosSuministros/V_07/'
        'SuministroFactEmitidas.wsdl'
    )
    port_name = 'SuministroFactEmitidas'
    if test:
        port_name += 'Pruebas'

    cli = _get_client(wsdl, crt, pkey, test)

    return _IssuedInvoiceService(
        cli.bind('siiService', port_name))


def bind_recieved_invoices_service(crt, pkey, test=False):
    wsdl = (
        'http://www.agenciatributaria.es/static_files/AEAT/'
        'Contenidos_Comunes/La_Agencia_Tributaria/Modelos_y_formularios/'
        'Suministro_inmediato_informacion/FicherosSuministros/V_07/'
        'SuministroFactRecibidas.wsdl'
    )
    port_name = 'SuministroFactRecibidas'
    if test:
        port_name += 'Pruebas'

    cli = _get_client(wsdl, crt, pkey, test)

    return _RecievedInvoiceService(
        cli.bind('siiService', port_name))


class _IssuedInvoiceService(object):
    def __init__(self, service):
        self.service = service

    def submit(self, headers, invoices, mapper=None):
        body = (
            map(mapper.build_submit_request, invoices)
            if mapper
            else invoices
        )
        _logger.debug(body)
        response_ = self.service.SuministroLRFacturasEmitidas(
            headers, body)
        _logger.debug(response_)
        return response_

    def cancel(self, headers, invoices, mapper=None):
        body = (
            map(mapper.build_delete_request, invoices)
            if mapper
            else invoices
        )
        _logger.debug(body)
        response_ = self.service.AnulacionLRFacturasEmitidas(
            headers, body)
        _logger.debug(response_)
        return response_

    def query(self, headers, year=None, period=None):
        filter_ = build_query_filter(year=year, period=period)
        _logger.debug(filter_)
        response_ = self.service.ConsultaLRFacturasEmitidas(
            headers, filter_)
        _logger.debug(response_)
        return response_


class _RecievedInvoiceService(object):
    def __init__(self, service):
        self.service = service

    def submit(self, headers, invoices, mapper=None):
        body = (
            map(mapper.build_submit_request, invoices)
            if mapper
            else invoices
        )
        _logger.debug(body)
        response_ = self.service.SuministroLRFacturasRecibidas(
            headers, body)
        _logger.debug(response_)
        return response_

    def cancel(self, headers, invoices, mapper=None):
        body = (
            map(mapper.build_delete_request, invoices)
            if mapper
            else invoices
        )
        _logger.debug(body)
        response_ = self.service.AnulacionLRFacturasRecibidas(
            headers, body)
        _logger.debug(response_)
        return response_

    def query(self, headers, year=None, period=None):
        filter_ = build_query_filter(year=year, period=period)
        _logger.debug(filter_)
        response_ = self.service.ConsultaLRFacturasRecibidas(
            headers, filter_)
        _logger.debug(response_)
        return response_
