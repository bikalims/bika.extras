# -*- coding: utf-8 -*-
"""Tests for the custom setup-data importers."""

import os
import unittest

from Products.CMFCore.utils import getToolByName
from openpyxl import load_workbook
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from senaite.core.tests.layers import BASE_TESTING

from bika.extras.browser.overrides.setupdata import Analysis_Services


class Loader(object):
    """Minimal setup-data loader context required by worksheet importers."""

    def __init__(self, context):
        self.context = context


class TestAnalysisServiceSetupDataImport(unittest.TestCase):

    layer = BASE_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def test_imports_new_analysis_attributes(self):
        workbook = os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            "..",
            "setupdata",
            "Dream Test set",
            "Dream Test set - Updated Analysis Attributes.xlsx",
        ))

        setup_data = load_workbook(filename=workbook)
        importer = Analysis_Services(self.portal)
        importer(
            Loader(self.portal),
            setup_data,
            "bika.extras",
            "Dream Test set - Updated Analysis Attributes",
        )

        catalog = getToolByName(self.portal, "senaite_catalog_setup")
        brains = catalog(
            portal_type="AnalysisService",
            title="Chloride",
        )
        self.assertTrue(brains)
        service = brains[0].getObject()

        self.assertEqual("numeric", service.getResultType())
        self.assertEqual(
            {"days": 4, "hours": 3, "minutes": 2},
            service.getMaxHoldingTime(),
        )
        self.assertEqual("0.05", service.getLowerDetectionLimit())
        self.assertEqual("1000", service.getUpperDetectionLimit())
        self.assertEqual(
            "0.100000", service.getLowerLimitOfQuantification())
        self.assertEqual(
            "900.000000", service.getUpperLimitOfQuantification())
