# -*- coding: utf-8 -*-
"""Init and utils."""
import logging
from zope.i18nmessageid import MessageFactory

from bika.lims.api import get_request
from bika.extras.interfaces import IBikaExtrasLayer

PRODUCT_NAME = "bika.extras"
PROFILE_ID = "profile-{}:default".format(PRODUCT_NAME)
logger = logging.getLogger(PRODUCT_NAME)

_ = MessageFactory(PRODUCT_NAME)


def is_installed():
    """Returns whether the product is installed or not"""
    request = get_request()
    return IBikaExtrasLayer.providedBy(request)
