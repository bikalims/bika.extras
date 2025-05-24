# -*- coding: utf-8 -*-

from plone.memoize import view

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.worksheet.views.analyses import AnalysesView as AV
from bika.lims.interfaces import IDuplicateAnalysis
from bika.lims.interfaces import IReferenceAnalysis
from bika.lims.interfaces import IRoutineAnalysis
from bika.lims.utils import t
from bika.lims.utils import get_image


class AnalysesView(AV):
    def __init__(self, context, request):
        super(AnalysesView, self).__init__(context, request)
        self.show_column_toggles = True
        self.columns['Attachments']["toggle"] = False
        self.columns['retested']["title"] = _("Retested")

    @view.memoize
    def get_slot_header_data(self, obj):
        """Prepare the data for the slot header template
        """

        item_obj = None
        item_title = ""
        item_url = ""
        item_img = ""
        item_img_url = ""
        item_img_text = ""
        additional_item_icons = []

        parent_obj = None
        parent_title = ""
        parent_url = ""
        parent_img = ""
        parent_img_text = ""
        additional_parent_icons = []

        sample_type = None
        sample_type_title = ""
        sample_type_url = ""
        sample_type_img = ""
        sample_type_img_text = ""

        sample_point = None
        sample_point_title = ""
        sample_point_url = ""
        sample_point_img = ""
        sample_point_img_text = ""

        if IDuplicateAnalysis.providedBy(obj):
            # item
            request = obj.getRequest()
            reference_analysis_group_id = obj.getReferenceAnalysesGroupID()
            item_obj = request
            item_title = "{}".format(reference_analysis_group_id)
            item_url = api.get_url(request)
            item_img = "duplicate.png"
            item_img_url = api.get_url(request)
            item_img_text = t(_("Duplicate"))
            # additional item icons
            additional_item_icons.append(
                self.render_remarks_tag(request))
            # parent
            client = request.getClient()
            parent_obj = client
            parent_title = api.get_title(client)
            parent_url = api.get_url(client)
            parent_img = "client.png"
            parent_img_text = t(_("Client"))
            # sample type
            sample_type = request.getSampleType()
            sample_type_title = request.getSampleTypeTitle()
            sample_type_url = api.get_url(sample_type)
            sample_type_img = "sampletype.png"
            sample_type_img_text = t(_("Sample Type"))
            # sample point
            sample_point = request.getSamplePoint()
            if sample_point:
                sample_point_title = request.getSamplePointTitle()
                sample_point_url = api.get_url(sample_point)
                sample_point_img = "samplepoint.png"
                sample_point_img_text = t(_("Sample Point"))
        elif IReferenceAnalysis.providedBy(obj):
            # item
            sample = obj.getSample()
            item_obj = sample
            reference_analysis_group_id = obj.getReferenceAnalysesGroupID()
            item_title = "%s" % (reference_analysis_group_id)
            item_url = api.get_url(sample)
            item_img_url = api.get_url(sample)
            item_img = "control.png"
            item_img_text = t(_("Control"))
            if obj.getReferenceType() == "b":
                item_img = "blank.png"
                item_img_text = t(_("Blank"))
            # parent
            supplier = obj.getSupplier()
            parent_obj = supplier
            parent_title = api.get_title(supplier)
            parent_url = api.get_url(supplier)
            parent_img = "supplier.png"
            parent_img_text = t(_("Supplier"))
        elif IRoutineAnalysis.providedBy(obj):
            # item
            request = obj.getRequest()
            item_obj = request
            item_title = api.get_id(request)
            item_url = api.get_url(request)
            item_img = "sample.png"
            item_img_url = api.get_url(request)
            item_img_text = t(_("Sample"))
            # additional item icons
            additional_item_icons.append(
                self.render_remarks_tag(request))
            # parent
            client = obj.getClient()
            parent_obj = client
            parent_title = api.get_title(client)
            parent_url = api.get_url(client)
            parent_img = "client.png"
            parent_img_text = t(_("Client"))
            # sample type
            sample_type = obj.getSampleType()
            sample_type_title = obj.getSampleTypeTitle()
            sample_type_url = api.get_url(sample_type)
            sample_type_img = "sampletype.png"
            sample_type_img_text = t(_("Sample Type"))

            # sample point
            sample_point = request.getSamplePoint()
            if sample_point:
                sample_point_title = request.getSamplePointTitle()
                sample_point_url = api.get_url(sample_point)
                sample_point_img = "samplepoint.png"
                sample_point_img_text = t(_("Sample Point"))

        return {
            # item
            "item_obj": item_obj,
            "item_title": item_title,
            "item_url": item_url,
            "item_img": get_image(item_img, title=item_img_text),
            "item_img_url": item_img_url,
            "additional_item_icons": additional_item_icons,
            # parent
            "parent_obj": parent_obj,
            "parent_title": parent_title,
            "parent_url": parent_url,
            "parent_img": get_image(parent_img, title=parent_img_text),
            "additional_parent_icons": additional_parent_icons,
            # sample type
            "sample_type_obj": sample_type,
            "sample_type_title": sample_type_title,
            "sample_type_url": sample_type_url,
            "sample_type_img": get_image(
                sample_type_img, title=sample_type_img_text),
            # sample point
            "sample_point_obj": sample_point,
            "sample_point_title": sample_point_title,
            "sample_point_url": sample_point_url,
            "sample_point_img": get_image(
                sample_point_img, title=sample_point_img_text),
        }
