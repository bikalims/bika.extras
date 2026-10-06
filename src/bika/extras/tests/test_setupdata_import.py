# -*- coding: utf-8 -*-
"""Tests for the custom setup-data importers."""

import os
import shutil
import tempfile
import unittest

from Products.CMFCore.utils import getToolByName
from openpyxl import load_workbook
from openpyxl import Workbook
from bika.lims import api
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from senaite.core.tests.layers import BASE_TESTING
from senaite.core.tests.layers import BASE_LAYER_FIXTURE

from bika.extras.browser.overrides.setupdata import Analysis_Services
from bika.extras.browser.overrides.setupdata import Methods
from bika.extras.browser.overrides.setupdata import Sample_Types


class MethodSupplierLayer(PloneSandboxLayer):
    defaultBases = (BASE_LAYER_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import bika.coa.extenders
        self.loadZCML(package=bika.coa.extenders, name="methodsupplier.zcml")

    def setUpPloneSite(self, portal):
        from bika.coa.setuphandlers import add_method_supplier_behavior
        add_method_supplier_behavior(portal)


METHOD_SUPPLIER_TESTING = FunctionalTesting(
    bases=(MethodSupplierLayer(),), name="BIKA:MethodSupplierTesting")


class Loader(object):
    """Minimal setup-data loader context required by worksheet importers."""

    def __init__(self, context):
        self.context = context


class TestSampleTypeSetupDataImport(unittest.TestCase):
    layer = BASE_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def import_sample_type(self, headers, values):
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Sample Types"
        sheet.append(headers)
        sheet.append(["Column descriptions"])
        sheet.append(["Column types"])
        sheet.append(values)
        Sample_Types(self.portal)(Loader(self.portal), workbook,
                                 "bika.extras", "uploaded")
        catalog = getToolByName(self.portal, "senaite_catalog_setup")
        return catalog(portal_type="SampleType", title=values[0])[0].getObject()

    def test_missing_hazardous_column(self):
        sample_type = self.import_sample_type(
            ["title", "Prefix", "MinimumVolume", "RetentionPeriod"],
            ["Minimal type", "MT", "250 g", 30])
        self.assertFalse(sample_type.getHazardous())
        self.assertEqual({"days": 30, "hours": 0, "minutes": 0},
                         sample_type.getRetentionPeriod())

    def test_explicit_optional_values_are_preserved(self):
        sample_type = self.import_sample_type(
            ["title", "Hazardous", "Prefix", "MinimumVolume",
             "RetentionPeriod"],
            ["Hazardous type", "True", "HZ", "10 ml", 7])
        self.assertTrue(sample_type.getHazardous())
        self.assertEqual("HZ", sample_type.getPrefix())
        self.assertEqual("10 ml", sample_type.getMinimumVolume())
        self.assertEqual({"days": 7, "hours": 0, "minutes": 0},
                         sample_type.getRetentionPeriod())


class TestMethodSetupDataImport(unittest.TestCase):
    layer = METHOD_SUPPLIER_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

    def import_workbook(self, workbook):
        Methods(self.portal)(Loader(self.portal), workbook,
                             "bika.extras", "Dream Test set")

    def test_dream_methods_keep_instructions_and_supplier(self):
        from bika.coa.extenders.methodsupplier import IMethodSupplier
        from bika.coa.extenders.methodsupplier import get_method_supplier
        workbook = load_workbook(os.path.join(
            os.path.dirname(__file__), "..", "setupdata", "Dream Test set",
            "Dream Test set.xlsx"))
        supplier = api.create(self.portal.setup.suppliers, "Supplier",
                              title=u"Lab ZEX")
        self.import_workbook(workbook)
        methods = self.portal.setup.methods.objectValues()
        self.assertEqual(10, len(methods))
        method = next(m for m in methods if m.Title() == "APHA 1001 Metals")
        self.assertEqual(u"Dolar summer set", method.getInstructions().raw)
        self.assertFalse(method.getAccredited())
        self.assertEqual(supplier, IMethodSupplier(method).supplier)
        self.assertEqual(supplier, get_method_supplier(method))
        self.assertEqual(api.get_uid(supplier),
                         IMethodSupplier(method).getRawSupplier())

    def test_optional_sheet_duplicate_ids_and_calculation(self):
        calculation = api.create(self.portal.setup.calculations, "Calculation",
                                 title=u"Test calculation")
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Methods"
        sheet.append(["title", "MethodID", "Calculation_title", "Accredited"])
        sheet.append([])
        sheet.append([])
        sheet.append(["First", "same-id", "Test calculation", "False"])
        sheet.append(["Second", "same-id", "", "True"])
        self.import_workbook(workbook)
        methods = {m.Title(): m for m in
                   self.portal.setup.methods.objectValues()}
        self.assertEqual("same-id", methods["First"].getMethodID())
        self.assertEqual("", methods["Second"].getMethodID())
        self.assertEqual(calculation, methods["First"].getCalculation())
        self.assertEqual([calculation], methods["First"].getCalculations())
        self.assertFalse(methods["First"].getAccredited())
        self.assertTrue(methods["Second"].getAccredited())

    def test_instrument_relations_and_dx_document(self):
        from bika.extras.browser.overrides import setupdata
        instrument = api.create(self.portal.bika_setup.bika_instruments,
                                "Instrument", title=u"Test instrument")
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Methods"
        sheet.append(["title", "Instrument_title", "MethodDocument"])
        sheet.append([])
        sheet.append([])
        sheet.append(["Document method", "Test instrument", "method.txt"])
        sheet.append(["Missing document", "", "missing.txt"])
        links = workbook.create_sheet("Instrument Methods")
        links.append(["Method_title", "Instrument_title"])
        links.append([])
        links.append([])
        links.append(["Document method", "Test instrument"])
        directory = tempfile.mkdtemp()
        original = setupdata.resource_filename
        try:
            with open(os.path.join(directory, "method.txt"), "wb") as stream:
                stream.write("Method instructions")
            setupdata.resource_filename = lambda project, path: os.path.join(
                directory, os.path.basename(path))
            self.import_workbook(workbook)
        finally:
            setupdata.resource_filename = original
            shutil.rmtree(directory)
        methods = {m.Title(): m for m in
                   self.portal.setup.methods.objectValues()}
        method = methods["Document method"]
        self.assertEqual([instrument], method.getInstruments())
        self.assertIn(method, instrument.getMethods())
        self.assertEqual("Method instructions", method.getMethodDocument().data)
        self.assertEqual(u"method.txt", method.getMethodDocument().filename)
        self.assertIsNone(methods["Missing document"].getMethodDocument())

    def test_behavior_enablement_and_legacy_supplier_upgrade(self):
        from bika.coa.extenders.methodsupplier import IMethodSupplier
        from bika.coa.setuphandlers import add_method_supplier_behavior
        from bika.coa.upgrade.v02_07_01 import upgrade
        fti = self.portal.portal_types["Method"]
        original = tuple(fti.behaviors)
        add_method_supplier_behavior(self.portal)
        self.assertEqual(original, tuple(fti.behaviors))
        supplier = api.create(self.portal.setup.suppliers, "Supplier",
                              title=u"Legacy supplier")
        method = api.create(self.portal.setup.methods, "Method",
                            title=u"Migrated method")
        method.Supplier = api.get_uid(supplier)
        upgrade(self.portal.portal_setup)
        self.assertEqual(supplier, IMethodSupplier(method).supplier)
        upgrade(self.portal.portal_setup)
        self.assertEqual(supplier, IMethodSupplier(method).supplier)

    def test_method_listing_uses_supplier_behavior(self):
        from bika.coa.extenders.methodsupplier import IMethodSupplier
        from bika.extras.browser.listingview import methods as listing_module
        from senaite.core.browser.controlpanel.methods.view import MethodsView
        supplier = api.create(self.portal.setup.suppliers, "Supplier",
                              title=u"Listing supplier")
        method = api.create(self.portal.setup.methods, "Method",
                            title=u"Listed method", method_id=u"LIST-1")
        IMethodSupplier(method).supplier = supplier
        listing = MethodsView(self.portal.setup.methods, self.portal.REQUEST)
        adapter = listing_module.MethodsListingViewAdapter(
            listing, self.portal.setup.methods)
        original = listing_module.is_installed
        listing_module.is_installed = lambda: True
        try:
            adapter.before_render()
            adapter.before_render()
            for state in listing.review_states:
                self.assertEqual(1, state["columns"].count("Subcontractor"))
                self.assertEqual(1, state["columns"].count("MethodID"))
            item = adapter.folder_item(method, {"replace": {}}, 0)
            self.assertEqual("LIST-1", item["MethodID"])
            self.assertEqual("Listing supplier", item["Subcontractor"])
            self.assertIn(supplier.absolute_url(),
                          item["replace"]["Subcontractor"])
            IMethodSupplier(method).supplier = None
            item = adapter.folder_item(method, {"replace": {}}, 0)
            self.assertEqual("", item["Subcontractor"])
            self.portal.portal_types["Method"].behaviors = tuple(
                b for b in self.portal.portal_types["Method"].behaviors
                if b != "bika.coa.method_supplier")
            item = adapter.folder_item(method, {"replace": {}}, 0)
            self.assertEqual("", item["Subcontractor"])
        finally:
            listing_module.is_installed = original


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
