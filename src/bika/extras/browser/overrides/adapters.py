# -*- coding: utf-8 -*-

from senaite.core.browser.form.adapters.analysisservice import (
    EditForm as EF
)


class AnalysisServiceEditForm(EF):
    def can_change_keyword(self, keyword):
        """Check if the keyword can be changed

        Writable if no active analyses exist with the given keyword
        """
        query = {
            "portal_type": "Analysis",
            "is_active": True,
            "getKeyword": keyword}
        brains = self.analysis_catalog(query)
        return len(brains) == 0
