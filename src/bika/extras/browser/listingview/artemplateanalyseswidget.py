# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from zope.component import adapts
from zope.interface import implements

from bika.extras import is_installed
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class ARTemplateAnalysesListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context
        self.an_cats = None
        self.an_cats_order = None

    def before_render(self):
        if not is_installed():
            return
        if self.listing.show_categories_enabled():
            self.categories = []
            self.listing.show_categories = True
            self.listing.expand_all_categories = False

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item
        return item

    def folderitems(self):
        """Sort by Categories"""
        bsc = getToolByName(self.context, "senaite_catalog_setup")
        self.an_cats = bsc(
            portal_type="AnalysisCategory", sort_on="sortable_title"
        )
        self.an_cats_order = dict(
            [(b.Title, "{:04}".format(a)) for a, b in enumerate(self.an_cats)]
        )
        items = super(ARTemplateAnalysesListingViewAdapter, self).folderitems()
        if self.show_categories_enabled():
            self.categories = map(
                lambda x: x[0], sorted(self.categories, key=lambda x: x[1])
            )
        else:
            self.categories.sort()
        return items
