
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
    tax_reagyp_rate = methodcaller('get', 'tax_reagyp_rate')
    tax_reagyp_amount = methodcaller('get', 'tax_reagyp_amount')


def test_simple_mapping():
    invoice = {
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
            'tax_rate': .21,
            'tax_base': 100,
            'tax_amount': 21,
            'tax_equivalence_surcharge_rate': .052,
            'tax_equivalence_surcharge_amount': 5.2,
        }, {
            'tax_rate': .10,
            'tax_base': 10,
            'tax_amount': 1,
        }],
    }

    mapper = RecievedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)

    assert request_['PeriodoImpositivo']['Periodo'] == '05'
    assert request_['IDFactura']['FechaExpedicionFacturaEmisor'] == '31-12-2017'
    taxes = request_['FacturaRecibida']['DesgloseFactura']['DesgloseIVA']['DetalleIVA']
    assert len(taxes) == 2
    assert taxes[0]['BaseImponible'] == 100
    assert taxes[1]['BaseImponible'] == 10
    assert taxes[0]['TipoImpositivo'] == 21
    assert taxes[1]['TipoImpositivo'] == 10
    assert taxes[0]['TipoRecargoEquivalencia'] == 5.2
    assert taxes[1].get('TipoRecargoEquivalencia') is None
    assert 'PorcentCompensacionREAGYP' not in taxes[0]
    assert 'ImporteCompensacionREAGYP' not in taxes[0]
    assert 'ImporteRectificacion' not in request_['FacturaRecibida']
    assert 'FacturasRectificadas' not in request_['FacturaRecibida']
    assert 'FacturasRectificadas' not in request_['FacturaRecibida']
    assert 'IDOtro' not in request_['FacturaRecibida']['Contraparte']
    assert request_['FacturaRecibida']['Contraparte']['NIF'] == request_['IDFactura']['IDEmisorFactura']['NIF']
    assert request_['FacturaRecibida']['Contraparte']['NIF'] == '00000011B'


def test_foreign_counterpart():
    invoice = {
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
        'counterpart_id_type': '04',
        'counterpart_country': 'FR',
        'taxes': [{
            'tax_rate': .21,
            'tax_base': 100,
            'tax_amount': 21,
            'tax_equivalence_surcharge_rate': .052,
            'tax_equivalence_surcharge_amount': 5.2,
        }, {
            'tax_rate': .10,
            'tax_base': 10,
            'tax_amount': 1,
        }],
    }

    mapper = RecievedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)

    counterpart = request_['FacturaRecibida']['Contraparte']
    invoice_issuer = request_['IDFactura']['IDEmisorFactura']
    assert 'NIF' not in counterpart
    assert 'NIF' not in invoice_issuer
    counterpart_id = counterpart['IDOtro']
    issuer_id = invoice_issuer['IDOtro']
    assert counterpart_id['IDType'] == issuer_id['IDType'] == '04'
    assert counterpart_id['CodigoPais'] == issuer_id['CodigoPais'] == 'FR'
    assert counterpart_id['ID'] == issuer_id['ID'] == '00000011B'


def test_reagyp_mapping():
    invoice = {
        'year': 2017,
        'period': 5,
        'nif': '00000010X',
        'serial_number': 1,
        'issue_date': date(year=2017, month=12, day=31),
        'move_date': date(year=2017, month=12, day=31),
        'deductible_amount': 50,
        'invoice_kind': 'L1',
        'specialkey_or_trascendence': '02',
        'description': 'My Description',
        'not_exempt_kind': 'S1',
        'counterpart_name': 'Counterpart',
        'counterpart_nif': '00000011B',
        'counterpart_id_type': '01',
        'counterpart_country': 'ES',
        'taxes': [{
            'tax_rate': .21,
            'tax_base': 100,
            'tax_amount': 21,
            'tax_reagyp_rate': .12,
            'tax_reagyp_amount': 12,
        }],
    }
    mapper = RecievedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)

    taxes = request_['FacturaRecibida']['DesgloseFactura']['DesgloseIVA']['DetalleIVA']

    assert 'BaseImponible' in taxes[0]
    assert 'TipoImpositivo' not in taxes[0]
    assert 'CuotaSuportada' not in taxes[0]
    assert 'TipoRecargoEquivalencia' not in taxes[0]
    assert 'TipoRecargoEquivalencia' not in taxes[0]
    assert 'CuotaRecargoEquivalencia' not in taxes[0]
    assert taxes[0]['PorcentCompensacionREAGYP'] == 12
    assert taxes[0]['ImporteCompensacionREAGYP'] == 12


def test_intracommunitary_subjected():
    invoice = {
        'year': 2017,
        'period': 5,
        'nif': '00000010X',
        'serial_number': 1,
        'issue_date': date(year=2017, month=12, day=31),
        'move_date': date(year=2017, month=12, day=31),
        'invoice_kind': 'L1',
        'specialkey_or_trascendence': '09',
        'description': 'My Description',
        'not_exempt_kind': 'S1',
        'counterpart_name': 'Counterpart',
        'counterpart_nif': 'FR00000011B',
        'counterpart_id_type': '02',
        'counterpart_country': 'FR',
        'untaxed_amount': 100,
        'total_amount': 100,
        'taxes': [{
            'tax_rate': .21,
            'tax_base': 100,
            'tax_amount': 21,
        }, {
            'tax_rate': -0.21,
            'tax_base': 100,
            'tax_amount': -21,
        }],
    }

    mapper = RecievedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)

    counterpart = request_['FacturaRecibida']['Contraparte']
    invoice_issuer = request_['IDFactura']['IDEmisorFactura']
    print request_
    taxes = request_['FacturaRecibida']['DesgloseFactura'][
        'DesgloseIVA']['DetalleIVA']
    assert len(taxes) == 2
    assert taxes[0]['BaseImponible'] == 100
    assert taxes[0]['TipoImpositivo'] == 21
    assert taxes[0]['CuotaSoportada'] == 21
    assert taxes[1]['BaseImponible'] == 100
    assert taxes[1]['TipoImpositivo'] == 21
    assert taxes[1]['CuotaSoportada'] == -21
    assert 'NIF' not in counterpart
    assert 'NIF' not in invoice_issuer
    counterpart_id = counterpart['IDOtro']
    issuer_id = invoice_issuer['IDOtro']
    assert counterpart_id['IDType'] == issuer_id['IDType'] == '02'
    assert counterpart_id['CodigoPais'] == issuer_id['CodigoPais'] == 'FR'
    assert counterpart_id['ID'] == issuer_id['ID'] == 'FR00000011B'


def test_intracommunitary_exempt():
    invoice = {
        'year': 2017,
        'period': 5,
        'nif': '00000010X',
        'serial_number': 1,
        'issue_date': date(year=2017, month=12, day=31),
        'move_date': date(year=2017, month=12, day=31),
        'invoice_kind': 'L1',
        'specialkey_or_trascendence': '01',
        'description': 'My Description',
        'exempt_kind': 'E5',
        'counterpart_name': 'Counterpart',
        'counterpart_nif': 'FR00000011B',
        'counterpart_id_type': '02',
        'counterpart_country': 'FR',
        'untaxed_amount': 100,
        'total_amount': 100,
        'taxes': [],
    }

    mapper = RecievedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)
    print request_
    counterpart = request_['FacturaRecibida']['Contraparte']
    invoice_issuer = request_['IDFactura']['IDEmisorFactura']
    taxes = request_['FacturaRecibida']['DesgloseFactura'][
        'DesgloseIVA']['DetalleIVA']
    assert len(taxes) == 1
    assert taxes[0]['BaseImponible'] == 100
    assert request_['FacturaRecibida']['ImporteTotal'] == 100
    assert 'NIF' not in counterpart
    assert 'NIF' not in invoice_issuer
    counterpart_id = counterpart['IDOtro']
    issuer_id = invoice_issuer['IDOtro']
    assert counterpart_id['IDType'] == issuer_id['IDType'] == '02'
    assert counterpart_id['CodigoPais'] == issuer_id['CodigoPais'] == 'FR'
    assert counterpart_id['ID'] == issuer_id['ID'] == 'FR00000011B'
