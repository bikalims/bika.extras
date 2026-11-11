# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.extras import is_installed
from bika.extras.config import _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class ReferenceDefinitionsListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return

        self.listing.columns["Analyses"] = {
            "title": _("Analyses"),
            "sortable": False,
            "toggle": True,
        }
        for state in self.listing.review_states:
            columns = state["columns"]
            if "Analyses" not in columns:
                columns.insert(columns.index("Title") + 1, "Analyses")

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        obj = api.get_object(obj)
        titles = []
        seen = set()
        for result in obj.getReferenceResults():
            uid = result.get("uid")
            if not uid or uid in seen:
                continue
            seen.add(uid)
            service = api.get_object_by_uid(uid, default=None)
            if service is not None:
                titles.append(api.get_title(service))
        item["Analyses"] = u", ".join(sorted(titles, key=lambda x: x.lower()))
        return item
