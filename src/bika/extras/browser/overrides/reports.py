# -*- coding: utf-8 -*-

from Products.CMFPlone.utils import get_installer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import ram

from bika.lims import api
from bika.reports.browser.reports import AdministrationView as AV
from bika.reports.browser.reports.selection_macros import _cache_key_select_client
from bika.reports.browser.reports.selection_macros import \
    SelectionMacrosView as SMV

from senaite.core.catalog import CLIENT_CATALOG


class SelectionMacrosView(SMV):

    @ram.cache(_cache_key_select_client)
    def select_client(self, style=None):
        client_catalog = api.get_tool(CLIENT_CATALOG)
        self.style = style
        self.clients = client_catalog(
            portal_type='Client', sort_on='sortable_title')
        return self.select_client_pt()


class AdministrationView(AV):
    """ Administration View form
    """
    template = ViewPageTemplateFile("templates/administration.pt")

    def is_senaite_crms_installed(self):
        qi = get_installer(self.portal)
        return qi.is_product_installed("senaite.crms")
