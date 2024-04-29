# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from bika.lims.browser.worksheet.views.results import ManageResultsView as MRV
from senaite.core.catalog import WORKSHEET_CATALOG


class ManageResultsView(MRV):
    template = ViewPageTemplateFile("templates/results.pt")

    def getAnalysesCategories(self):
        if not self.context.bika_setup.WorksheetTitle:
            return
        query = {
            "UID": self.context.UID(),
        }
        brains = api.search(query, WORKSHEET_CATALOG)
        if not brains:
            return
        return ", ".join(brains[0].getAnalysesCategories)
