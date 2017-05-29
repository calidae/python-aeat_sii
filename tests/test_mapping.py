
from datetime import date
from operator import methodcaller

from pyAEATsii import mapping


class IssuedTestInvoiceMapper(mapping.IssuedInvoiceMapper):
        year = methodcaller('get', 'year')
        period = methodcaller('get', 'period')
        nif = methodcaller('get', 'nif')
        serial_number = methodcaller('get', 'serial_number')
        issue_date = methodcaller('get', 'issue_date')
        invoice_kind = methodcaller('get', 'invoice_kind')
        rectified_invoice_kind = methodcaller('get', 'rectified_invoice_kind')
        rectified_base = methodcaller('get', 'rectified_base')
        rectified_amount = methodcaller('get', 'rectified_amount')
        total_amount = methodcaller('get', 'total_amount')
        specialkey_or_trascendence = methodcaller('get', 'specialkey_or_trascendence')
        description = methodcaller('get', 'description')
        not_exempt_kind = methodcaller('get', 'not_exempt_kind')
        counterpart_name = methodcaller('get', 'counterpart_name')
        counterpart_nif = methodcaller('get', 'counterpart_nif')
        counterpart_id_type = methodcaller('get', 'counterpart_id_type')
        counterpart_country = methodcaller('get', 'counterpart_country')
        taxes = methodcaller('get', 'taxes')
        tax_rate = methodcaller('get', 'tax_rate')
        tax_base = methodcaller('get', 'tax_base')
        tax_amount = methodcaller('get', 'tax_amount')


class RecievedTestInvoiceMapper(mapping.RecievedInvoiceMapper):
        year = methodcaller('get', 'year')
        period = methodcaller('get', 'period')
        nif = methodcaller('get', 'nif')
        serial_number = methodcaller('get', 'serial_number')
        issue_date = methodcaller('get', 'issue_date')
        invoice_kind = methodcaller('get', 'invoice_kind')
        rectified_invoice_kind = methodcaller('get', 'rectified_invoice_kind')
        rectified_base = methodcaller('get', 'rectified_base')
        rectified_amount = methodcaller('get', 'rectified_amount')
        total_amount = methodcaller('get', 'total_amount')
        specialkey_or_trascendence = methodcaller('get', 'specialkey_or_trascendence')
        description = methodcaller('get', 'description')
        not_exempt_kind = methodcaller('get', 'not_exempt_kind')
        counterpart_name = methodcaller('get', 'counterpart_name')
        counterpart_nif = methodcaller('get', 'counterpart_nif')
        counterpart_id_type = methodcaller('get', 'counterpart_id_type')
        counterpart_country = methodcaller('get', 'counterpart_country')
        taxes = methodcaller('get', 'taxes')
        tax_rate = methodcaller('get', 'tax_rate')
        tax_base = methodcaller('get', 'tax_base')
        tax_amount = methodcaller('get', 'tax_amount')


def test_issued_invoice_mapping():
    invoice = {
        'year': 2017,
        'period': 5,
        'nif': '00000010X',
        'serial_number': 1,
        'issue_date': date(year=2017, month=12, day=31),
        'invoice_kind': 'L1',
        'specialkey_or_trascendence': '01',
        'description': 'My Description',
        'not_exempt_kind': 'S1',
        'counterpart_name': 'Counterpart',
        'counterpart_nif': '00000011B',
        'counterpart_id_type': '07',
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
    mapper = IssuedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)
    assert request_['PeriodoImpositivo']['Periodo'] == '05'
    assert request_['IDFactura']['FechaExpedicionFacturaEmisor'] == '31-12-2017'
    taxes = request_['FacturaExpedida']['TipoDesglose']['DesgloseFactura']['Sujeta']['NoExenta']['DesgloseIVA']['DetalleIVA']
    assert len(taxes) == 2
    assert taxes[0]['BaseImponible'] == 100
    assert taxes[1]['BaseImponible'] == 10
    assert 'ImporteRectificacion' not in request_['FacturaExpedida']
    assert 'FacturasRectificadas' not in request_['FacturaExpedida']


def test_rectified_issued_invoice_mapping():
    invoice = {
        'year': 2017,
        'period': 5,
        'nif': '00000010X',
        'serial_number': 1,
        'issue_date': date(year=2017, month=12, day=31),
        'invoice_kind': 'R1',
        'rectified_invoice_kind': 'S',
        'rectified_base': 100,
        'rectified_amount': 200,
        'specialkey_or_trascendence': '01',
        'description': 'My Description',
        'not_exempt_kind': 'S1',
        'counterpart_name': 'Counterpart',
        'counterpart_nif': '00000011B',
        'counterpart_id_type': '07',
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
    mapper = IssuedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)

    assert request_['FacturaExpedida']['TipoRectificativa'] == 'S'
    assert request_['FacturaExpedida']['ImporteRectificacion']['BaseRectificada'] == 100
    assert request_['FacturaExpedida']['ImporteRectificacion']['CuotaRectificada'] == 200


def test_rectified_by_difference_issued_invoice_mapping():
    invoice = {
        'year': 2017,
        'period': 5,
        'nif': '00000010X',
        'serial_number': 1,
        'issue_date': date(year=2017, month=12, day=31),
        'invoice_kind': 'R1',
        'rectified_invoice_kind': 'I',
        'specialkey_or_trascendence': '01',
        'description': 'My Description',
        'not_exempt_kind': 'S1',
        'counterpart_name': 'Counterpart',
        'counterpart_nif': '00000011B',
        'counterpart_id_type': '07',
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
    mapper = IssuedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)

    assert request_['FacturaExpedida']['TipoRectificativa'] == 'I'
    assert 'ImporteRectificacion' not in request_['FacturaExpedida']


def test_rectified_simplified_issued_invoice_with_1_line_mapping():
    invoice = {
        'year': 2017,
        'period': 5,
        'nif': '00000010X',
        'serial_number': 1,
        'issue_date': date(year=2017, month=12, day=31),
        'invoice_kind': 'R5',
        'rectified_invoice_kind': 'I',
        'specialkey_or_trascendence': '01',
        'description': 'My Description',
        'not_exempt_kind': 'S1',
        'counterpart_name': 'Counterpart',
        'counterpart_nif': '00000011B',
        'counterpart_id_type': '07',
        'counterpart_country': 'ES',
        'taxes': [{
            'tax_rate': 21,
            'tax_base': 0,
            'tax_amount': 0,
        }],
    }
    mapper = IssuedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)

    assert request_['FacturaExpedida']['TipoRectificativa'] == 'I'
    assert 'ImporteTotal' in request_['FacturaExpedida']
