# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.extras import is_installed
from bika.extras.config import _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class BatchesListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return

        num_samples = [
            ("getNumberOfSamples", {"toggle": False, "title": _("Samples")})
        ]
        creator = [("Creator", {"toggle": False, "title": _("Creator")})]
        self.listing.columns.update(num_samples)
        self.listing.columns.update(creator)
        for i in range(len(self.listing.review_states)):
            self.listing.review_states[i]["columns"].append(
                "getNumberOfSamples"
            )
            self.listing.review_states[i]["columns"].append("Creator")

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        full_object = api.get_object(obj)
        item["getNumberOfSamples"] = full_object.getNumberOfSamples()
        item["Creator"] = api.get_user_fullname(full_object.Creator())
        return item
