
from operator import methodcaller

from pyAEATsii import callback_utils


class BaseTestInvoiceMapper(object):
    year = methodcaller('get', 'year')
    period = methodcaller('get', 'period')
    nif = methodcaller('get', 'nif')
    serial_number = methodcaller('get', 'serial_number')
    final_serial_number = methodcaller('get', 'final_serial_number')
    issue_date = methodcaller('get', 'issue_date')
    invoice_kind = methodcaller('get', 'invoice_kind')
    rectified_invoice_kind = methodcaller('get', 'rectified_invoice_kind')
    rectified_base = methodcaller('get', 'rectified_base')
    rectified_amount = methodcaller('get', 'rectified_amount')
    total_amount = methodcaller('get', 'total_amount')
    specialkey_or_trascendence = \
        methodcaller('get', 'specialkey_or_trascendence')
    description = methodcaller('get', 'description')
    not_exempt_kind = methodcaller('get', 'not_exempt_kind')
    exempt_kind = methodcaller('get', 'exempt_kind')
    counterpart_name = methodcaller('get', 'counterpart_name')
    counterpart_nif = methodcaller('get', 'counterpart_nif')
    counterpart_id_type = methodcaller('get', 'counterpart_id_type')
    counterpart_country = methodcaller('get', 'counterpart_country')
    counterpart_id = counterpart_nif
    untaxed_amount = methodcaller('get', 'untaxed_amount')
    total_amount = methodcaller('get', 'total_amount')
    taxes = methodcaller('get', 'taxes')
    tax_rate = methodcaller('get', 'tax_rate')
    tax_base = methodcaller('get', 'tax_base')
    tax_amount = methodcaller('get', 'tax_amount')
    tax_equivalence_surcharge_rate = methodcaller('get', 'tax_equivalence_surcharge_rate')
    tax_equivalence_surcharge_amount = methodcaller('get', 'tax_equivalence_surcharge_amount')
