# -*- coding: utf-8 -*-

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims import api
from senaite.core.browser.worksheets.worksheet.manage_results import (
    ManageResultsView as MRV
)
from senaite.core.catalog import WORKSHEET_CATALOG


class ManageResultsView(MRV):
    template = ViewPageTemplateFile("templates/results.pt")

    def getAnalysesCategories(self):
        try:
            if not self.context.bika_setup.WorksheetTitle:
                return
        except AttributeError:
            return

        query = {
            "UID": self.context.UID(),
        }
        brains = api.search(query, WORKSHEET_CATALOG)
        if not brains:
            return
        return ", ".join(brains[0].getAnalysesCategories)
