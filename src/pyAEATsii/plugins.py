
__all__ = [
    'LoggingPlugin',
]

from logging import getLogger
from lxml import etree
from zeep import Plugin

_logger = getLogger(__name__)


class LoggingPlugin(Plugin):

    def ingress(self, envelope, http_headers, operation):
        _logger.debug('http_headers: %s', http_headers)
        _logger.debug('operation: %s', operation)
        _logger.debug('envelope: %s', etree.tostring(
            envelope, pretty_print=True))
        return envelope, http_headers

    def egress(self, envelope, http_headers, operation, binding_options):
        _logger.debug('http_headers: %s', http_headers)
        _logger.debug('operation: %s', operation)
        _logger.debug('envelope: %s', etree.tostring(
            envelope, pretty_print=True))
        return envelope, http_headers


# TODO: JSESSIONID Plugin
