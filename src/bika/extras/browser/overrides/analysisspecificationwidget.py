# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.browser.widgets.analysisspecificationwidget import \
    AnalysisSpecificationView as ASV


class AnalysisSpecificationView(ASV):
    """Specification listing with analysis service units.

    Keep category collection and ordering in the core listing so that its
    category groups match the categories assigned to the service rows.
    """

    def folderitem(self, obj, item, index):
        item = super(AnalysisSpecificationView, self).folderitem(
            obj, item, index)
        item["Unit"] = api.get_object(obj).Unit
        return item
