# -*- coding: utf-8 -*-
#
# This file is part of BIKA.EXTRAS.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.

import collections

from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.bika_listing import BikaListingView
from bika.lims.permissions import AddAnalysisProfile
from bika.lims.utils import get_link
from plone.app.content.browser.interfaces import IFolderContentsView
from plone.app.layout.globals.interfaces import IViewView
from zope.interface.declarations import implements
from zope.i18n.locales import locales


# TODO: Separate content and view into own modules!


class AnalysisProfilesView(BikaListingView):
    implements(IFolderContentsView, IViewView)

    def __init__(self, context, request):
        super(AnalysisProfilesView, self).__init__(context, request)

        self.catalog = "senaite_catalog_setup"
        self.contentFilter = {
            "portal_type": "AnalysisProfile",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(self.context),
                "depth": 1,
            }
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=AnalysisProfile",
                "permission": AddAnalysisProfile,
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Analysis Profiles"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/analysisprofile_big.png"
        )

        self.show_select_row = False
        self.show_select_column = True
        self.pagesize = 25
        self.currency_symbol = self.get_currency_symbol()
        self.decimal_mark = self.get_decimal_mark()

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Profile"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "Description",
                "toggle": True,}),
            ("ProfileKey", {
                "title": _("Profile Key"),
                "sortable": False,
                "toggle": True,}),
            ("Price", {
                "title": _("Price"),
                "sortable": False,
                "toggle": True,}),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"is_active": True},
                "transitions": [{"id": "deactivate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {'is_active': False},
                "transitions": [{"id": "activate"}, ],
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

        if not self.context.bika_setup.getShowPrices():
            for i in range(len(self.review_states)):
                self.review_states[i]["columns"].remove("Price")
            del self.columns['Price']


    def get_decimal_mark(self):
        """Returns the decimal mark
        """
        return self.context.bika_setup.getDecimalMark()


    def get_currency_symbol(self):
        """Returns the locale currency symbol
        """
        currency = self.context.bika_setup.getCurrency()
        locale = locales.getLocale("en")
        locale_currency = locale.numbers.currencies.get(currency)
        if locale_currency is None:
            return "$"
        return locale_currency.symbol


    def format_price(self, price):
        """Formats the price with the set decimal mark and correct currency
        """
        return u"{} {}{}{:02d}".format(
            self.currency_symbol,
            price[0],
            self.decimal_mark,
            price[1],
        )


    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.
        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        obj = api.get_object(obj)
        title = obj.Title()
        description = obj.Description()
        url = obj.absolute_url()
        user_roles = api.get_current_user().getRoles()
        if "Manager" in user_roles:
            financial_permissions = True
        else:
            financial_permissions = False

        item["replace"]["Title"] = get_link(url, value=title)
        item["Description"] = description
        item["ProfileKey"] = obj.getProfileKey()
        if financial_permissions:
            item["Price"] = self.format_price(obj.AnalysisProfilePrice)
        return item


