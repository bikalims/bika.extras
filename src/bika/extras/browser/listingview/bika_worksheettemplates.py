# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.lims.utils import get_link
from bika.extras import is_installed
from bika.extras.config import _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class WorksheetTemplatesListingViewAdapter(object):
    adapts(IListingView)
    implements(IListingViewAdapter)

    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return

        number_of_positions = [
            (
                "NumberOfPositions",
                {"toggle": True, "title": _("Number of Positions")},
            )
        ]
        blanks = [
            (
                "Blanks",
                {"toggle": True, "title": _("Blank")},
            )
        ]
        controls = [
            (
                "Controls",
                {"toggle": True, "title": _("Controls")},
            )
        ]
        number_of_duplicates = [
            (
                "NumberOfDuplicates",
                {"toggle": True, "title": _("Number Of Duplicates")},
            )
        ]
        self.listing.columns.update(number_of_positions)
        self.listing.columns.update(blanks)
        self.listing.columns.update(controls)
        self.listing.columns.update(number_of_duplicates)

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        obj = api.get_object(obj)

        # NumberOfPostions
        item["NumberOfPositions"] = len(obj.getLayout())

        Raw_layout = obj.getLayout()
        num = 0
        blanks = []
        controls = []
        controlUrls = []
        blankUrls = []
        for position in Raw_layout:
            if position.get("type") == "d":
                num = num + 1
            if position.get("type") == "b":
                blank_id = position.get("blank_ref")
                blank_obj = api.get_object_by_uid(blank_id)
                blank_title = blank_obj.Title()
                blank_url = api.get_url(blank_obj)
                if blank_title not in blanks:
                    blanks.append(blank_title)
                    blankUrls.append(get_link(blank_url, blank_title))
            if position.get("type") == "c":
                control_id = position.get("control_ref")
                control_obj = api.get_object_by_uid(control_id)
                control_title = control_obj.Title()
                control_url = api.get_url(control_obj)
                if control_title not in controls:
                    controls.append(control_title)
                    controlUrls.append(get_link(control_url, control_title))

        # Blanks
        if blanks:
            item["replace"]["Blanks"] = blankUrls

        # Controls
        if controls:
            item["replace"]["Controls"] = controlUrls

        # NummberOfDuplicates
        if num:
            item["NumberOfDuplicates"] = num
        return item
