# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.extras import is_installed
from bika.extras.config import _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class InstrumentsListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return
        for i in range(len(self.listing.review_states)):
            rmv = "WeeksToExpire"
            self.listing.review_states[i]["columns"].remove(rmv)
        del self.listing.columns["WeeksToExpire"]

        import_interface = [
            ("ImportInterface",
             {"toggle": True, "sortable": False,
              "title": _("Import Interface")},
             )
        ]
        export_interface = [
            ("ExportInterface",
                {"toggle": True, "sortable": False,
                 "title": _("Export Interface")},)
        ]
        self.listing.columns.update(import_interface)
        self.listing.columns.update(export_interface)

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        obj = api.get_object(obj)
        import_interface = obj.getImportDataInterface()
        import_interfaces_list = obj.getImportDataInterfacesList()
        if len(import_interface) > 1:
            for name in import_interface:
                if name:
                    item["replace"]["ImportInterface"] = \
                        import_interfaces_list.getValue(name)

        export_interfaces_list = obj.getExportDataInterfacesList()
        export_interface = obj.DataInterface
        if export_interface:
            item["replace"]["ExportInterface"] = \
                export_interfaces_list.getValue(export_interface)
        return item
