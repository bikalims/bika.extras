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
        specification = [
            ("Specification", {"toggle": False, "title": _("Specification")})
        ]
        self.listing.columns.update(specification)
        batch_title = [("BatchTitle", {"toggle": False, "title": _("Batch Title")})]
        self.listing.columns.update(batch_title)
        client_batch_id = [
            ("ClientBatchID", {"toggle": False, "title": _("Client Batch ID")})
        ]
        self.listing.columns.update(client_batch_id)
        for i in range(len(self.listing.review_states)):
            self.listing.review_states[i]["columns"].append("Container")
            self.listing.review_states[i]["columns"].append("Specification")
            self.listing.review_states[i]["columns"].append("BatchTitle")
            self.listing.review_states[i]["columns"].append("ClientBatchID")

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        full_object = api.get_object(obj)
        # Container
        container = full_object.getContainer()
        if container:
            container_title = container.Title()
            container_url = container.absolute_url()
            container_link = get_link(container_url, container_title)
            item["Container"] = container_title
            item["replace"]["Container"] = container_link

        # Specification
        specification = full_object.getSpecification()
        if specification:
            spec_title = specification.Title()
            spec_url = specification.absolute_url()
            spec_link = get_link(spec_url, spec_title)
            item["Specification"] = spec_title
            item["replace"]["Specification"] = spec_link

        batch = full_object.getBatch()
        # BatchTitle
        if batch:
            batch_title = batch.title
            batch_url = batch.absolute_url()
            batch_link = get_link(batch_url, batch_title)
            item["BatchTitle"] = batch_title
            item["replace"]["BatchTitle"] = batch_link

        # ClientBatchID
        if batch:
            batch_title = batch.getClientBatchID()
            batch_url = batch.absolute_url()
            batch_link = get_link(batch_url, batch_title)
            item["ClientBatchID"] = batch_title
            item["replace"]["ClientBatchID"] = batch_link

        return item
