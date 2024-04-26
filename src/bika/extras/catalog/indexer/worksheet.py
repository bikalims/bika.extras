# -*- coding: utf-8 -*-

from bika.lims.interfaces import IWorksheet
from plone.indexer import indexer


@indexer(IWorksheet)
def getAnalysesCategories(instance):
    analyses = instance.getAnalyses()
    categories = []
    for analysis in analyses:
        category_title = analysis.getCategoryTitle()
        if category_title not in categories:
            categories.append(category_title)
    return categories
