# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.lims.utils import get_link
from bika.extras import is_installed
from bika.extras.config import _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class MethodsListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return

        method_id = [("MethodID", {"toggle": False, "title": _("Method ID")})]
        subcontractor = [
            ("Subcontractor", {"toggle": False, "title": _("Subcontractor")})
        ]
        self.listing.columns.update(method_id)
        self.listing.columns.update(subcontractor)
        for i in range(len(self.listing.review_states)):
            self.listing.review_states[i]["columns"].append("MethodID")
            self.listing.review_states[i]["columns"].append("Subcontractor")

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item
        obj = api.get_object(obj)
        # MethodID
        method_id = obj.getMethodID()
        if method_id:
            method_id_title = method_id.title()
            method_id_url = obj.absolute_url()
            method_id_link = get_link(method_id_url, method_id_title)
            item["MethodID"] = method_id_title
            item["replace"]["MethodID"] = method_id_link
        # Subcontractor
        supplier_uid = obj["Supplier"]
        if supplier_uid:
            supplier_obj = api.get_object_by_uid(supplier_uid)
            subcontractor_title = supplier_obj.Title()
            subcontractor_url = supplier_obj.absolute_url()
            subcontractor_link = get_link(
                subcontractor_url, subcontractor_title
            )
            item["Subcontractor"] = subcontractor_title
            item["replace"]["Subcontractor"] = subcontractor_link
        return item
