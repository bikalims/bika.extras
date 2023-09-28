# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.lims.utils import get_link
from bika.extras import is_installed
from bika.extras.config import _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class SamplesListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return

        container = [("Container", {"toggle": False, "title": _("Container")})]
        self.listing.columns.update(container)
        for i in range(len(self.listing.review_states)):
            self.listing.review_states[i]["columns"].append("Container")

        for i in self.listing.review_states:
            if i["title"] == "Dispatched":
                i["title"] = "Disposed"

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        full_object = api.get_object(obj)
        container = full_object.getContainer()
        if container:
            container_title = container.Title()
            container_url = container.absolute_url()
            container_link = get_link(container_url, container_title)
            item["Container"] = container_title
            item["replace"]["Container"] = container_link
        return item
