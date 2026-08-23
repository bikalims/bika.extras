# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.lims.utils import get_link_for
from bika.extras import is_installed
from bika.extras.config import _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class WorksheetsListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return

        instrument = [
            ("Instrument", {"toggle": False, "title": _("Instrument")})
        ]
        self.listing.columns.update(instrument)
        for review_state in self.listing.review_states:
            review_state["columns"].append("Instrument")

        try:
            if not self.context.bika_setup.WorksheetTitle:
                return
        except AttributeError:
            return

        categories = [("Categories", {"toggle": False, "title": _("Categories")})]
        self.listing.columns.update(categories)
        for i in range(len(self.listing.review_states)):
            self.listing.review_states[i]["columns"].append("Categories")

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        worksheet = api.get_object(obj)
        instrument = worksheet.getInstrument()
        if instrument:
            item["Instrument"] = api.get_title(instrument)
            item["replace"]["Instrument"] = get_link_for(instrument)

        try:
            if not self.context.bika_setup.WorksheetTitle:
                return item
        except AttributeError:
            return item

        item["Categories"] = ", ".join(obj.getAnalysesCategories or [])
        return item
