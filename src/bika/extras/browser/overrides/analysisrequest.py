# -*- coding: utf-8 -*-

from bika.lims import api
from bika.lims.browser.analysisrequest.tables import FieldAnalysesTable as FAT
from bika.lims.browser.analysisrequest.tables import LabAnalysesTable as LAT


class FieldAnalysesTable(FAT):
    def __init__(self, context, request):
        super(FieldAnalysesTable, self).__init__(context, request)

        self.contentFilter.update({
            "getPointOfCapture": "field",
            "getAncestorsUIDs": [api.get_uid(context)]
        })

        self.form_id = "%s_field_analyses" % api.get_id(context)
        self.allow_edit = True
        self.show_workflow_action_buttons = True
        self.show_select_column = True
        self.show_search = False
        self.expand_all_categories = False
        self.show_column_toggles = True
        self.reorder_analysis_columns()


class LabAnalysesTable(LAT):
    def __init__(self, context, request):
        super(LabAnalysesTable, self).__init__(context, request)

        self.contentFilter.update({
            "getPointOfCapture": "lab",
            "getAncestorsUIDs": [api.get_uid(context)]
        })

        self.form_id = "%s_lab_analyses" % api.get_id(context)
        self.allow_edit = True
        self.show_workflow_action_buttons = True
        self.show_select_column = True
        self.show_search = False
        self.show_column_toggles = True
        self.expand_all_categories = False
        self.reorder_analysis_columns()
