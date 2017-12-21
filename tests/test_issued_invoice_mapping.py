
from datetime import date

from pyAEATsii import mapping

from .mapping import BaseTestInvoiceMapper


class IssuedTestInvoiceMapper(
        mapping.IssuedInvoiceMapper,
        BaseTestInvoiceMapper
):
    pass


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
        'counterpart_id_type': '01',
        'counterpart_country': 'ES',
        'untaxed_amount': 110,
        'total_amount': 132,
        'taxes': [{
            'tax_rate': .21,
            'tax_base': 100,
            'tax_amount': 21,
        }, {
            'tax_rate': .10,
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
    assert taxes[0]['TipoImpositivo'] == 21
    assert taxes[1]['TipoImpositivo'] == 10
    assert 'ImporteRectificacion' not in request_['FacturaExpedida']
    assert 'FacturasRectificadas' not in request_['FacturaExpedida']
    assert 'FacturasRectificadas' not in request_['FacturaExpedida']
    assert 'IDOtro' not in request_['FacturaExpedida']['Contraparte']
    assert request_['FacturaExpedida']['Contraparte']['NIF'] == '00000011B'
    assert request_['FacturaExpedida']['DescripcionOperacion'] == \
        "My Description"


def test_uncensed_counterpart():
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
        'untaxed_amount': 110,
        'total_amount': 132,
        'taxes': [{
            'tax_rate': .21,
            'tax_base': 100,
            'tax_amount': 21,
        }, {
            'tax_rate': .10,
            'tax_base': 10,
            'tax_amount': 1,
        }],
    }
    mapper = IssuedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)
    assert 'NIF' not in request_['FacturaExpedida']['Contraparte']
    assert request_['FacturaExpedida']['Contraparte']['IDOtro']['ID'] == '00000011B'


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
        'untaxed_amount': 110,
        'total_amount': 132,
        'taxes': [{
            'tax_rate': .21,
            'tax_base': 100,
            'tax_amount': 21,
        }, {
            'tax_rate': .10,
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
        'untaxed_amount': 110,
        'total_amount': 132,
        'taxes': [{
            'tax_rate': .21,
            'tax_base': 100,
            'tax_amount': 21,
        }, {
            'tax_rate': .10,
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
        'untaxed_amount': 0,
        'total_amount': 0,
        'taxes': [{
            'tax_rate': .21,
            'tax_base': 0,
            'tax_amount': 0,
        }],
    }
    mapper = IssuedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)

    assert request_['FacturaExpedida']['TipoRectificativa'] == 'I'
    assert 'ImporteTotal' in request_['FacturaExpedida']


def test_summary_issued_invoice_id():
    """
    Test that if invoice kind is "F4" the final serial number appears
    in the invoice id
    """
    invoice = {
        'year': 2017,
        'period': 5,
        'nif': '00000010X',
        'serial_number': 1,
        'final_serial_number': 'FINAL_ID',
        'issue_date': date(year=2017, month=12, day=31),
        'invoice_kind': 'F4',
        'specialkey_or_trascendence': '01',
        'description': 'My Description',
        'not_exempt_kind': 'S1',
        'counterpart_name': 'Counterpart',
        'counterpart_nif': '00000011B',
        'counterpart_id_type': '07',
        'counterpart_country': 'ES',
        'untaxed_amount': 110,
        'total_amount': 132,
        'taxes': [{
            'tax_rate': .21,
            'tax_base': 100,
            'tax_amount': 21,
        }, {
            'tax_rate': .10,
            'tax_base': 10,
            'tax_amount': 1,
        }],
    }
    mapper = IssuedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)

    assert request_['IDFactura']['NumSerieFacturaEmisorResumenFin'] == 'FINAL_ID'


def test_issued_invoice_inv_subj_pass_mapping():
    invoice = {
        'year': 2017,
        'period': 5,
        'nif': '00000010X',
        'serial_number': 1,
        'issue_date': date(year=2017, month=12, day=31),
        'invoice_kind': 'F1',
        'specialkey_or_trascendence': '01',
        'description': 'My Description',
        'not_exempt_kind': 'S2',
        'counterpart_name': 'Counterpart',
        'counterpart_nif': '00000011B',
        'counterpart_id_type': '01',
        'counterpart_country': 'ES',
        'untaxed_amount': 100,
        'total_amount': 100,
        'taxes': [],
    }
    mapper = IssuedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)
    assert request_['PeriodoImpositivo']['Periodo'] == '05'
    assert request_['IDFactura']['FechaExpedicionFacturaEmisor'] == \
        '31-12-2017'
    taxes = request_['FacturaExpedida']['TipoDesglose'][
        'DesgloseFactura']['Sujeta']['NoExenta'][
        'DesgloseIVA']['DetalleIVA']
    assert len(taxes) == 1
    assert taxes[0]['BaseImponible'] == 100
    assert taxes[0]['TipoImpositivo'] == 0
    assert 'NoSujeta' not in request_['FacturaExpedida']['TipoDesglose'][
        'DesgloseFactura']
    assert 'ImporteRectificacion' not in request_['FacturaExpedida']
    assert 'FacturasRectificadas' not in request_['FacturaExpedida']
    assert 'FacturasRectificadas' not in request_['FacturaExpedida']
    assert 'NIF' in request_['FacturaExpedida']['Contraparte']
    assert request_['FacturaExpedida']['Contraparte']['NIF'] == \
        '00000011B'


def test_issued_invoice_inv_subj_pass_intra_mapping():
    invoice = {
        'year': 2017,
        'period': 5,
        'nif': '00000010X',
        'serial_number': 1,
        'issue_date': date(year=2017, month=12, day=31),
        'invoice_kind': 'F1',
        'specialkey_or_trascendence': '01',
        'description': 'My Description',
        'not_exempt_kind': 'S2',
        'counterpart_name': 'Counterpart',
        'counterpart_nif': 'LT00000011B',
        'counterpart_id_type': '02',
        'counterpart_country': 'LT',
        'untaxed_amount': 100,
        'total_amount': 100,
        'taxes': [],
    }
    mapper = IssuedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)
    assert request_['PeriodoImpositivo']['Periodo'] == '05'
    assert request_['IDFactura']['FechaExpedicionFacturaEmisor'] == \
        '31-12-2017'
    assert 'DesgloseFactura' not in request_['FacturaExpedida']['TipoDesglose']
    taxes = request_['FacturaExpedida']['TipoDesglose'][
        'DesgloseTipoOperacion']['Entrega']['Sujeta']['NoExenta'][
        'DesgloseIVA']['DetalleIVA']
    assert len(taxes) == 1
    assert taxes[0]['BaseImponible'] == 100
    assert taxes[0]['TipoImpositivo'] == 0
    assert request_['FacturaExpedida']['TipoDesglose'][
        'DesgloseTipoOperacion']['Entrega']['NoSujeta'][
        'ImporteTAIReglasLocalizacion'] == 100
    assert 'ImporteRectificacion' not in request_['FacturaExpedida']
    assert 'FacturasRectificadas' not in request_['FacturaExpedida']
    assert 'FacturasRectificadas' not in request_['FacturaExpedida']
    assert 'IDOtro' in request_['FacturaExpedida']['Contraparte']
    assert request_['FacturaExpedida']['Contraparte']['IDOtro']['ID'] == \
        'LT00000011B'


def test_issued_invoice_goods_intra_mapping():
    invoice = {
        'year': 2017,
        'period': 5,
        'nif': '00000010X',
        'serial_number': 1,
        'issue_date': date(year=2017, month=12, day=31),
        'invoice_kind': 'L1',
        'specialkey_or_trascendence': '01',
        'description': 'My Description',
        'not_exempt_kind': None,
        'exempt_kind': 'E5',
        'counterpart_name': 'Counterpart',
        'counterpart_nif': 'LT00000011B',
        'counterpart_id_type': '02',
        'counterpart_country': 'LT',
        'untaxed_amount': 100,
        'total_amount': 100,
        'taxes': [],
    }
    mapper = IssuedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)
    assert request_['PeriodoImpositivo']['Periodo'] == '05'
    assert request_['IDFactura']['FechaExpedicionFacturaEmisor'] == \
        '31-12-2017'
    assert request_['FacturaExpedida']['TipoDesglose'][
        'DesgloseTipoOperacion']['Entrega']['Sujeta']['Exenta'][
        'BaseImponible'] == 100
    assert 'ImporteRectificacion' not in request_['FacturaExpedida']
    assert 'FacturasRectificadas' not in request_['FacturaExpedida']
    assert 'FacturasRectificadas' not in request_['FacturaExpedida']
    assert 'IDOtro' in request_['FacturaExpedida']['Contraparte']
    assert request_['FacturaExpedida']['Contraparte']['IDOtro']['ID'] == \
        'LT00000011B'


def test_issued_invoice_first_semester_mapping():
    invoice = {
        'year': 2017,
        'period': 5,
        'nif': '00000010X',
        'serial_number': 1,
        'issue_date': date(year=2017, month=3, day=15),
        'invoice_kind': 'L1',
        'specialkey_or_trascendence': '16',  # "Primer semestre"
        'description': 'My Description',
        'not_exempt_kind': 'S1',
        'counterpart_name': 'Counterpart',
        'counterpart_nif': '00000011B',
        'counterpart_id_type': '01',
        'counterpart_country': 'ES',
        'untaxed_amount': 110,
        'total_amount': 132,
        'taxes': [{
            'tax_rate': .21,
            'tax_base': 100,
            'tax_amount': 21,
        }, {
            'tax_rate': .10,
            'tax_base': 10,
            'tax_amount': 1,
        }],
    }
    mapper = IssuedTestInvoiceMapper()
    request_ = mapper.build_submit_request(invoice)
    assert (
        request_['FacturaExpedida']['DescripcionOperacion'] ==
        "Registro del Primer semestre"
    )
