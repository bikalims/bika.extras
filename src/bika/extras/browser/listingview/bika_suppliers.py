# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.lims.utils import get_link
from bika.extras import is_installed
from bika.extras.config import _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class SuppliersListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return
        for i in range(len(self.review_states)):
            self.listing.review_states[i]["columns"].remove("Fax")
        if "Fax" in self.listing.columns:
            del self.listing.columns["Fax"]

        contacts = [
            ("Contacts",
             {"toggle": True, "sortable": False,
              "title": _("Contacts")},
             )
        ]
        self.listing.columns.update(contacts)

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        obj = api.get_object(obj)
        children = obj.values()
        contacts_url = "{}/{}".format(item['url'], "contacts")
        contacts = []
        number_of_contacts = 0

        for child in children:
            if child.portal_type == "SupplierContact":
                number_of_contacts = number_of_contacts + 1
                if number_of_contacts > 2:
                    contacts.append(get_link(contacts_url, "..."))
                    break
                child_url = child.absolute_url()
                child_name = child.getFullname()
                contacts.append(get_link(child_url, child_name))

        item["Contacts"] = contacts
        return item
