# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

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

        if not self.context.bika_setup.WorksheetTitle:
            return
        categories = [("Categories", {"toggle": False, "title": _("Categories")})]
        self.listing.columns.update(categories)
        for i in range(len(self.listing.review_states)):
            self.listing.review_states[i]["columns"].append("Categories")

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item
        if not self.context.bika_setup.WorksheetTitle:
            return item

        item["Categories"] = ", ".join(obj.getAnalysesCategories)
        return item
