# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.extras import is_installed
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class AnalysisRequestAnalysesListViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return
        import pdb; pdb.set_trace()
        self.do_cats = self.context.bika_setup.getCategoriseAnalysisServices()
        if self.do_cats:
            self.listing.contentFilter["sort_on"] = "category_sort_key"
            self.listing.show_categories = True
            self.listing.expand_all_categories = False

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item
        return item

    def folderitems(self):
        items = super(AnalysisRequestAnalysesListViewAdapter, self).folderitems()
        return items
