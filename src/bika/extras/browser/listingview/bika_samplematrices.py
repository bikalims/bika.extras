# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.extras import is_installed
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class SampleMatricesListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return
        self.listing.contentFilter["sort_order"] = "ascending"

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item
        return item
