# -*- coding: utf-8 -*-
import unittest

from contextlib import contextmanager
from bika.extras.browser.overrides.analysisspecificationwidget import \
    AnalysisSpecificationView
from bika.lims.browser.widgets import analysisspecificationwidget as core


class Record(object):
    def __init__(self, **values):
        self.__dict__.update(values)


class Service(object):
    Unit = "%"

    def __init__(self, category):
        self.category = category

    def getKeyword(self):
        return "Fe"

    def getCategoryTitle(self):
        return self.category

    def getMethods(self):
        return []

    def getAccredited(self):
        return False

    def getAttachmentRequired(self):
        return False


@contextmanager
def replace_attribute(obj, name, value):
    original = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield
    finally:
        setattr(obj, name, original)


class TestAnalysisSpecificationView(unittest.TestCase):

    def check_listing(self, categorised):
        view = AnalysisSpecificationView.__new__(AnalysisSpecificationView)
        view.show_categories_enabled = lambda: categorised
        view.categories = []
        view.found_categories = []
        view.get_dynamic_analysisspecs = lambda: {}
        view.specification = {"Fe": {"min": "40", "max": "60"}}
        view.min_operator_choices = []
        view.max_operator_choices = []
        view.allow_edit = True
        services = [Service("Metals"), Service("General")]

        def folderitems(listing):
            return [listing.folderitem(service, {
                "before": {}, "after": {}, "replace": {}, "choices": {}}, i)
                for i, service in enumerate(services)]

        catalog = lambda query: [Record(Title="General"),
                                 Record(Title="Metals")]
        with replace_attribute(core.BikaListingView, "folderitems", folderitems), \
                replace_attribute(core.api, "get_object", lambda x: x), \
                replace_attribute(core.api, "get_url", lambda x: "/service"), \
                replace_attribute(core.api, "get_title", lambda x: "Iron"), \
                replace_attribute(core.api, "get_tool", lambda x: catalog):
            items = view.folderitems()

        self.assertEqual(len(items), 2)
        for item in items:
            self.assertEqual(item["Unit"], "%")
            self.assertEqual(item["Keyword"], "Fe")
            self.assertEqual(item["min"], "40")
            self.assertEqual(item["max"], "60")
            self.assertTrue(item["selected"])
        if categorised:
            self.assertEqual(view.categories, ["General", "Metals"])
            self.assertEqual([x["category"] for x in items],
                             ["Metals", "General"])
        else:
            self.assertEqual(view.categories, [])
            self.assertTrue(all("category" not in x for x in items))

    def test_categorised_services_keep_rows_and_catalog_category_order(self):
        self.check_listing(True)

    def test_uncategorised_services_keep_rows(self):
        self.check_listing(False)
