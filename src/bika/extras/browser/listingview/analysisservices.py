# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements
from zope.i18n.locales import locales

from bika.lims import api
from bika.extras import is_installed
from bika.extras.config import _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class AnalysisServicesListingViewAdapter(object):
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

        description = [
            (
                "Description",
                {"toggle": False, "sortable": False, "title": _("Description")},
            )
        ]
        commercial_id = [
            (
                "CommercialID",
                {"toggle": False, "sortable": False, "title": _("Commercial ID")},
            )
        ]
        decimal_precision = [
            (
                "DecimalPrecision",
                {"toggle": False, "sortable": False, "title": _("Decimal Precision")},
            )
        ]
        protocol_id = [
            (
                "ProtocolID",
                {"toggle": False, "sortable": False, "title": _("Protocol ID")},
            )
        ]
        price = [("Price", {"toggle": False, "sortable": False, "title": _("Price")})]
        vat = [("Vat", {"toggle": False, "sortable": False, "title": _("VAT %")})]
        bulk_price = [
            (
                "BulkPrice",
                {"toggle": False, "sortable": False, "title": _("Bulk Price")},
            )
        ]
        hidden = [
            ("Hidden", {"toggle": False, "sortable": False, "title": _("Hidden")})
        ]

        self.listing.columns.update(description)
        self.listing.columns.update(commercial_id)
        self.listing.columns.update(decimal_precision)
        self.listing.columns.update(protocol_id)
        self.listing.columns.update(price)
        self.listing.columns.update(vat)
        self.listing.columns.update(bulk_price)
        self.listing.columns.update(hidden)

        for i in range(len(self.listing.review_states)):
            self.listing.review_states[i]["columns"].append("Description")
            self.listing.review_states[i]["columns"].append("CommercialID")
            self.listing.review_states[i]["columns"].append("DecimalPrecision")
            self.listing.review_states[i]["columns"].append("ProtocolID")
            self.listing.review_states[i]["columns"].append("Price")
            self.listing.review_states[i]["columns"].append("Vat")
            self.listing.review_states[i]["columns"].append("BulkPrice")
            self.listing.review_states[i]["columns"].append("Hidden")

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        obj = api.get_object(obj)

        # Description
        description = obj.Description()
        if description:
            description_value = description
            item["Description"] = description_value

        # CommercialID
        commercial_id = obj.getCommercialID()
        if commercial_id:
            commercial_id_value = commercial_id
            item["CommercialID"] = commercial_id_value

        # DecimalPrecision
        decimal_precision = obj.Precision
        if decimal_precision:
            decimal_precision_value = decimal_precision
            item["DecimalPrecision"] = decimal_precision_value

        # ProtocolID
        protocol_id = obj.ProtocolID
        if protocol_id:
            protocol_id_value = protocol_id
            item["ProtocolID"] = protocol_id_value

        # Vat
        vat = obj.VAT
        if vat:
            if vat[1] != 0:
                vat_value = u"{}{}{}".format(vat[0], self.decimal_mark, vat[1])
            else:
                vat_value = vat[0]
            item["Vat"] = vat_value

        # BulkPrice
        bulk_price = obj.getBulkPrice()
        if bulk_price:
            bulk_price_value = bulk_price
            item["BulkPrice"] = self.format_price(bulk_price_value)

        # Hidden
        hidden = obj.Hidden
        hidden_value = _("Yes") if hidden else _("")
        item["Hidden"] = hidden_value

        return item

    def get_decimal_mark(self):
        """Returns the decimal mark"""
        return self.context.bika_setup.getDecimalMark()

    def get_currency_symbol(self):
        """Returns the locale currency symbol"""
        currency = self.context.bika_setup.getCurrency()
        locale = locales.getLocale("en")
        locale_currency = locale.numbers.currencies.get(currency)
        if locale_currency is None:
            return "$"
        return locale_currency.symbol

    def format_price(self, price):
        """Formats the price with the set decimal mark and correct currency"""
        # convert float price to list
        price_list = str(price).split(self.decimal_mark)
        # LIMS-1052
        if not price_list:
            return

        try:
            decimal_places = len(price_list[1])
            if decimal_places < 2:
                output = u"{} {}{}{:02d}".format(
                    self.currency_symbol,
                    int(price_list[0]),
                    self.decimal_mark,
                    int(price_list[1]),
                )
            else:
                output = u"{} {}{}{}".format(
                    self.currency_symbol,
                    int(price_list[0]),
                    self.decimal_mark,
                    int(price_list[1]),
                )
        except Exception:
            return

        return output
