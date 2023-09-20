# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements
from zope.i18n.locales import locales

from bika.lims import api
from bika.extras import is_installed
from bika.extras.config import _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class AnalysisProfilesListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context
        self.currency_symbol = self.get_currency_symbol()
        self.decimal_mark = self.get_decimal_mark()

    def before_render(self):
        if not is_installed():
            return
        self.listing.contentFilter["path"] = \
            {"query": api.get_path(self.context),
             "depth": 1,
             }
        if not self.context.bika_setup.getShowPrices():
            for i in range(len(self.listing.review_states)):
                if "Price" in self.listing.review_states[i]["columns"]:
                    self.listing.review_states[i]["columns"].remove("Price")
            if "Price" in self.listing.columns:
                del self.listing.columns['Price']
            return

        price = [
            ("Price",
             {"toggle": False, "sortable": False, "title": _("Price")},
             )
        ]
        self.listing.columns.update(price)
        for i in range(len(self.listing.review_states)):
            self.listing.review_states[i]["columns"].append("Price")
        self.currency_symbol = self.get_currency_symbol()
        self.decimal_mark = self.get_decimal_mark()

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        financial_permissions = False
        user_roles = api.get_current_user().getRoles()
        if "Manager" in user_roles:
            financial_permissions = True

        obj = api.get_object(obj)
        if financial_permissions:
            item["Price"] = self.format_price(obj.AnalysisProfilePrice)
        return item

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
