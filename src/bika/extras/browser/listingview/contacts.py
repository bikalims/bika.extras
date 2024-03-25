# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.lims.utils import get_link
from bika.extras.config import _
from bika.extras import is_installed
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class ClientContactsListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return
        self.listing.contentFilter["sort_order"] = "descending"

        cc_contacts = [("CCContacts", {"toggle": False, "title": _("CC Contacts")})]
        self.listing.columns.update(cc_contacts)
        for i in range(len(self.listing.review_states)):
            self.listing.review_states[i]["columns"].append("CCContacts")

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        obj = api.get_object(obj)
        cc_contacts = obj.getCCContact()
        if cc_contacts:
            links = map(
                lambda c: get_link(c.absolute_url(),
                                   value = c.Title(),
                                   css_class = "link"),
                cc_contacts)
            item["replace"]["CCContacts"] = ", ".join(links)

        return item
