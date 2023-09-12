# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.extras import is_installed
from bika.extras.config import _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class CalculationsListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return
        interim_fields = [
            ("InterimFields", {"toggle": False, "title": _("Interim Fields")},)
        ]
        self.listing.columns.update(interim_fields)

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        obj = api.get_object(obj)
        interim_fields_dict = obj.InterimFields
        interim_fields = []
        if interim_fields_dict:
            for interim in interim_fields_dict:
                interim_fields.append(interim.get("title"))
        item["InterimFields"] = interim_fields

        return item
