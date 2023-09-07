# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer

from bika.extras import PRODUCT_NAME
from bika.extras import logger
from senaite.core.catalog import SETUP_CATALOG
from senaite.core.setuphandlers import setup_other_catalogs

# Tuples of (catalog, index_name, index_attribute, index_type)
INDEXES = [
    (SETUP_CATALOG, "category_sort_key", "", "KeywordIndex"),
]

# Tuples of (catalog, column_name)
COLUMNS = []


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'bika.extras:uninstall',
        ]


def setup_handler(context):
    """Generic setup handler"""
    if context.readDataFile("{}.txt".format(PRODUCT_NAME)) is None:
        return

    logger.info("{} setup handler [BEGIN]".format(PRODUCT_NAME.upper()))
    portal = context.getSite()

    # Setup catalogs
    setup_catalogs(portal)

    logger.info("{} setup handler [DONE]".format(PRODUCT_NAME.upper()))


def post_install(context):
    """Post install script"""
    # Do something at the end of the installation of this package.


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.


def setup_catalogs(portal):
    """Setup catalogs"""
    setup_other_catalogs(portal, indexes=INDEXES, columns=COLUMNS)
