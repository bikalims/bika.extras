# -*- coding: utf-8 -*-

from bika.lims.interfaces import IAnalysisService
from plone.indexer import indexer
from senaite.core.catalog.utils import sortable_sortkey_title


@indexer(IAnalysisService)
def category_sort_key(instance):
    if instance.getCategory():
        category_sort_key = sortable_sortkey_title(instance.getCategory())
        return category_sort_key
    return None
