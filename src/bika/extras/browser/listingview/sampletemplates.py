# -*- coding: utf-8 -*-

from zope.component import adapts
from zope.interface import implements

from bika.lims import api
from bika.lims.utils import get_link
from bika.extras import is_installed
from bika.extras.config import _
from senaite.app.listing.interfaces import IListingView
from senaite.app.listing.interfaces import IListingViewAdapter


class SampleTemplatesListingViewAdapter(object):
    def __init__(self, listing, context):
        self.listing = listing
        self.context = context

    def before_render(self):
        if not is_installed():
            return
        sample_point = [
            (
                "SamplePointTitle",
                {"toggle": False, "sortable": False, "title": _("Sample Point")},
            )
        ]
        sample_type = [
            (
                "SampleTypeTitle",
                {"toggle": False, "sortable": False, "title": _("Sample Type")},
            )
        ]
        composite = [
            ("Composite", {"toggle": False, "sortable": False, "title": _("Composite")})
        ]
        lab_sample = [
            (
                "LabSample",
                {"toggle": False, "sortable": False, "title": _("Lab Sample")},
            )
        ]
        partitions = [
            (
                "Partitions",
                {"toggle": False, "sortable": False, "title": _("Partitions")},
            )
        ]
        self.listing.columns.update(sample_point)
        self.listing.columns.update(sample_type)
        self.listing.columns.update(composite)
        self.listing.columns.update(lab_sample)
        self.listing.columns.update(partitions)
        for i in range(len(self.listing.review_states)):
            self.listing.review_states[i]["columns"].append("SamplePointTitle")
            self.listing.review_states[i]["columns"].append("SampleTypeTitle")
            self.listing.review_states[i]["columns"].append("Composite")
            self.listing.review_states[i]["columns"].append("LabSample")
            self.listing.review_states[i]["columns"].append("Partitions")

    def folder_item(self, obj, item, index):
        if not is_installed():
            return item

        obj = api.get_object(obj)

        # Sample Point
        sample_point = obj.getSamplePoint()
        if sample_point:
            sample_point_title = sample_point.Title()
            sample_point_url = sample_point.absolute_url()
            sample_point_link = get_link(sample_point_url, sample_point_title)
            item["SamplePointTitle"] = sample_point_title
            item["replace"]["SamplePointTitle"] = sample_point_link

        # Sample Type
        sample_type = obj.getSampleType()
        if sample_type:
            sample_type_title = sample_type.Title()
            sample_type_url = sample_type.absolute_url()
            sample_type_link = get_link(sample_type_url, sample_type_title)
            item["SampleTypeTitle"] = sample_type_title
            item["replace"]["SampleTypeTitle    "] = sample_type_link

        # Composite
        composite = obj.getComposite()
        composite_value = _("Yes") if composite else _("No")
        item["replace"]["Composite"] = composite_value

        # Lab Sample
        lab_sample = obj.getSamplingRequired()
        lab_sample_value = _("Yes") if lab_sample else _("No")
        item["replace"]["LabSample"] = lab_sample_value

        # Partitions
        all_partitions = obj.getPartitions()
        top_partitions = []
        if all_partitions:
            for partition in all_partitions:
                top_partitions.append(partition["part_id"])
                if len(top_partitions) > 1 and len(all_partitions) > 2:
                    top_partitions.append("...")
                    break
            formatted_top_partitions = ", ".join(top_partitions)
            sample_template_url = obj.absolute_url()
            top_partitions_link = get_link(
                sample_template_url, formatted_top_partitions
            )
            item["replace"]["Partitions"] = top_partitions_link

        return item
