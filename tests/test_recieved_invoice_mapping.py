
from datetime import date
from operator import methodcaller

from pyAEATsii import mapping

from .mapping import BaseTestInvoiceMapper


class RecievedTestInvoiceMapper(
        mapping.RecievedInvoiceMapper,
        BaseTestInvoiceMapper
):
    move_date = methodcaller('get', 'move_date')
    deductible_amount = methodcaller('get', 'deductible_amount')


_simple_invoice = {
    'year': 2017,
    'period': 5,
    'nif': '00000010X',
    'serial_number': 1,
    'issue_date': date(year=2017, month=12, day=31),
    'move_date': date(year=2017, month=12, day=31),
    'deductible_amount': 50,
    'invoice_kind': 'L1',
    'specialkey_or_trascendence': '01',
    'description': 'My Description',
    'not_exempt_kind': 'S1',
    'counterpart_name': 'Counterpart',
    'counterpart_nif': '00000011B',
    'counterpart_id_type': '01',
    'counterpart_country': 'ES',
    'taxes': [{
        'tax_rate': 21,
        'tax_base': 100,
        'tax_amount': 21,
    }, {
        'tax_rate': 10,
        'tax_base': 10,
        'tax_amount': 1,
    }],
}


def test_simple_mapping():
    mapper = RecievedTestInvoiceMapper()
    request_ = mapper.build_submit_request(_simple_invoice)
    assert request_['PeriodoImpositivo']['Periodo'] == '05'
    assert request_['IDFactura']['FechaExpedicionFacturaEmisor'] == '31-12-2017'
    taxes = request_['FacturaRecibida']['DesgloseFactura']['DesgloseIVA']['DetalleIVA']
    assert len(taxes) == 2
    assert taxes[0]['BaseImponible'] == 100
    assert taxes[1]['BaseImponible'] == 10
    assert 'PorcentCompensacionREAGYP' not in taxes[0]
    assert 'ImporteCompensacionREAGYP' not in taxes[0]
    assert 'ImporteRectificacion' not in request_['FacturaRecibida']
    assert 'FacturasRectificadas' not in request_['FacturaRecibida']
    assert 'FacturasRectificadas' not in request_['FacturaRecibida']
    assert 'IDOtro' not in request_['FacturaRecibida']['Contraparte']
    assert request_['FacturaRecibida']['Contraparte']['NIF'] == request_['IDFactura']['IDEmisorFactura']['NIF']
    assert request_['FacturaRecibida']['Contraparte']['NIF'] == '00000011B'
