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

        use_price = [("UsePrice", {"toggle": False, "title": _("Use Price")})]
        self.listing.columns.update(use_price)

        price = [
            ("Price",
             {"toggle": False, "sortable": False, "title": _("Price")},
             )
        ]
        self.listing.columns.update(price)
        commercialID = [("CommercialID", {"toggle": False, "title": _("Commercial ID")})]
        self.listing.columns.update(commercialID)
        vat = [("Vat", {"toggle": False, "title": _("VAT %")})]
        self.listing.columns.update(vat)

        for i in range(len(self.listing.review_states)):
            self.listing.review_states[i]["columns"].append("UsePrice")
            self.listing.review_states[i]["columns"].append("Price")
            self.listing.review_states[i]["columns"].append("CommercialID")
            self.listing.review_states[i]["columns"].append("Vat")
        self.currency_symbol = self.get_currency_symbol()
        self.decimal_mark = self.get_decimal_mark()

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        financial_permissions = False
        user_roles = api.get_current_user().getRoles()
        if "Manager" in user_roles:
            financial_permissions = True

        # Price
        obj = api.get_object(obj)
        if financial_permissions:
            item["Price"] = self.format_price(obj.AnalysisProfilePrice)

        # Commercial ID
        commercialID = obj.getCommercialID()
        item["CommercialID"] = commercialID

        # VAT
        vat = obj.getAnalysisProfileVAT()
        item["Vat"] = vat

        # Use Analysis Profile Price
        use_price = obj.getUseAnalysisProfilePrice()
        use_price_value = _("Yes") if use_price else _("No")
        item["UsePrice"] = use_price_value

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
        #convert float price to list
        price_list = str(price).split(self.decimal_mark)

        decimal_places = len(price_list[1])
        if decimal_places < 2:
            output = u"{} {}{}{:02d}".format(
            self.currency_symbol,
            int(price_list[0]),
            self.decimal_mark,
            int(price_list[1]))
        else:
            output = u"{} {}{}{}".format(
            self.currency_symbol,
            int(price_list[0]),
            self.decimal_mark,
            int(price_list[1]))
        return output
