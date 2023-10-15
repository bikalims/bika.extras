# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.lims.utils import get_email_link
from bika.lims.utils import get_link
from bika.extras import is_installed
from bika.extras.config import _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class ClientFolderContentsListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return
        if not self.context.bika_setup.getShowPrices():
            for i in range(len(self.listing.review_states)):
                bulk = "BulkDiscount"
                if bulk in self.listing.review_states[i]["columns"]:
                    self.listing.review_states[i]["columns"].remove(bulk)
                member_disc = "MemberDiscountApplies"
                if member_disc in self.listing.review_states[i]["columns"]:
                    self.listing.review_states[i]["columns"].remove(
                        member_disc
                    )
            if "MemberDiscountApplies" in self.listing.columns:
                del self.listing.columns["MemberDiscountApplies"]
            if "BulkDiscount" in self.listing.columns:
                del self.listing.columns["BulkDiscount"]

        if "MemberDiscountApplies" in self.listing.columns:
            self.listing.columns["MemberDiscountApplies"]["title"] = _(
                "Member Discount %"
            )

        contact = [
            (
                "Contacts",
                {"toggle": False, "sortable": False, "title": _("Contacts")},
            )
        ]
        fax = [
            (
                "Fax",
                {"toggle": False, "sortable": False, "title": _("Fax")},
            )
        ]
        self.listing.columns.update(contact)
        self.listing.columns.update(fax)

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        # Contacts
        obj = api.get_object(obj)
        all_contacts = obj.getContacts()
        contacts_url = "{}/{}".format(item["url"], "contacts")

        top_contacts = []
        if all_contacts:
            for contact in all_contacts:
                contact_url = contact.absolute_url()
                contact_name = contact.getFullname()
                top_contacts.append(get_link(contact_url, contact_name))
                if len(top_contacts) > 1 and len(all_contacts) > 2:
                    top_contacts.append(get_link(contacts_url, "..."))
                    break
        item["replace"]["Contacts"] = top_contacts

        # Client CC emails
        cc_email = obj.getCCEmails()
        if cc_email:
            item["replace"]["ClientCCEmails"] = get_email_link(cc_email)

        # Member discount %
        member_discount = api.get_setup().getMemberDiscount()
        if member_discount and obj.getMemberDiscountApplies():
            item["replace"]["MemberDiscountApplies"] = member_discount
        return item
