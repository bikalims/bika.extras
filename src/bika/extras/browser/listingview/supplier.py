# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.extras import is_installed
from bika.lims import api
from bika.lims.utils import get_email_link
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class ContactsListingViewAdapter(object):
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

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item
        obj = api.get_object(obj)
        email = obj.getEmailAddress()
        if email:
            item["replace"]["getEmailAddress"] = get_email_link(email)
        item["replace"]["getBusinessPhone"] = obj.getBusinessPhone()
        item["replace"]["getMobilePhone"] = obj.getMobilePhone()
        item["replace"]["getFax"] = obj.getBusinessFax()
        return item
