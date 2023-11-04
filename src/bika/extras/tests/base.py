# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.INSTRUMENTS
#
# Copyright 2018 by it's authors.

import unittest2 as unittest
from plone.app.testing import FunctionalTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing.bbb_at import PloneTestCase
from plone.testing import z2
from senaite.core.tests.layers import BASE_TESTING
from senaite.core.tests.layers import DATA_TESTING

from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFPlone.utils import _createObjectByType
from bika.lims import api
from bika.lims.idserver import renameAfterCreation
from bika.lims.utils import tmpID
from bika.lims.utils.analysisrequest import create_analysisrequest
from plone.protect.authenticator import createToken
from zope.event import notify
from zope.testbrowser.browser import Browser


class SimpleTestLayer(PloneSandboxLayer):
    """Setup Plone with installed AddOn only"""

    defaultBases = (
        BASE_TESTING,
        PLONE_FIXTURE,
    )

    def setUpZope(self, app, configurationContext):
        super(SimpleTestLayer, self).setUpZope(app, configurationContext)

        # Load ZCML
        import bika.lims
        import bika.extras

        self.loadZCML(package=bika.lims)
        self.loadZCML(package=bika.extras)

        # Install product and call its initialize() function
        z2.installProduct(app, "bika.extras")

    def setUpPloneSite(self, portal):
        super(SimpleTestLayer, self).setUpPloneSite(portal)

        # Apply Setup Profile (portal_quickinstaller)
        applyProfile(portal, "bika.lims:default")


###
# Use for simple tests (w/o contents)
###
SIMPLE_FIXTURE = SimpleTestLayer()
SIMPLE_TESTING = FunctionalTesting(
    bases=(SIMPLE_FIXTURE,), name="bika.extras:SimpleTesting"
)


class SimpleTestCase(unittest.TestCase):
    layer = SIMPLE_TESTING

    def setUp(self):
        super(SimpleTestCase, self).setUp()

        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["LabManager", "Manager"])


class FunctionalTestCase(unittest.TestCase):
    layer = SIMPLE_TESTING

    def setUp(self):
        super(FunctionalTestCase, self).setUp()

        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.request["ACTUAL_URL"] = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["LabManager", "Member"])


class BaseTestCase(PloneTestCase):
    """from senaite.core.tests.base.BaseTestCase"""

    layer = BASE_TESTING

    def setUp(self):
        super(BaseTestCase, self).setUp()
        self.request = self.layer["request"]
        self.request.form["_authenticator"] = createToken()
        self.request.environ["REQUEST_METHOD"] = "POST"
        self.portal.changeSkin("Plone Default")

    def getBrowser(
        self,
        username=TEST_USER_NAME,
        password=TEST_USER_PASSWORD,
        loggedIn=True,
    ):
        # Instantiate and return a testbrowser for convenience
        browser = Browser(self.portal)
        browser.addHeader("Accept-Language", "en-US")
        browser.handleErrors = False
        if loggedIn:
            browser.open(self.portal.absolute_url())
            browser.getControl("Login Name").value = username
            browser.getControl("Password").value = password
            browser.getControl("Log in").click()
            self.assertTrue("You are now logged in" in browser.contents)
        return browser

    def add_client(self, **kwargs):
        folder = self.portal.clients
        obj = _createObjectByType("Client", folder, tmpID())
        obj.edit(**kwargs)
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)
        notify(ObjectInitializedEvent(obj))
        return obj

    def add_contact(self, folder, **kwargs):
        obj = _createObjectByType("Contact", folder, tmpID())
        obj.edit(**kwargs)
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)
        notify(ObjectInitializedEvent(obj))
        return obj

    def add_manufacturer(self, **kwargs):
        folder = self.portal.bika_setup.bika_manufacturers
        obj = _createObjectByType("Manufacturer", folder, tmpID())
        obj.edit(**kwargs)
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)
        notify(ObjectInitializedEvent(obj))
        return obj

    def add_supplier(self, **kwargs):
        folder = self.portal.bika_setup.bika_suppliers
        obj = _createObjectByType("Supplier", folder, tmpID())
        obj.edit(**kwargs)
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)
        notify(ObjectInitializedEvent(obj))
        return obj

    def add_instrumenttype(self, **kwargs):
        folder = self.portal.bika_setup.bika_instrumenttypes
        obj = _createObjectByType("InstrumentType", folder, tmpID())
        obj.edit(**kwargs)
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)
        notify(ObjectInitializedEvent(obj))
        return obj

    def add_instrument(self, **kwargs):
        folder = self.portal.bika_setup.bika_instruments
        obj = _createObjectByType("Instrument", folder, tmpID())
        obj.edit(**kwargs)
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)
        notify(ObjectInitializedEvent(obj))
        return obj

    def add_analysiscategory(self, **kwargs):
        folder = self.portal.bika_setup.bika_analysiscategories
        obj = _createObjectByType("AnalysisCategory", folder, tmpID())
        obj.edit(**kwargs)
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)
        notify(ObjectInitializedEvent(obj))
        return obj

    def add_analysisservice(self, **kwargs):
        # service
        folder = self.portal.bika_setup.bika_analysisservices
        obj = _createObjectByType("AnalysisService", folder, tmpID())
        obj.edit(**kwargs)
        # done
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)
        notify(ObjectInitializedEvent(obj))

        return obj

    def add_calculation(self, **kwargs):
        folder = self.portal.bika_setup.bika_calculations
        obj = _createObjectByType("Calculation", folder, tmpID())
        obj.edit(**kwargs)
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)
        notify(ObjectInitializedEvent(obj))
        return obj

    def add_sampletype(self, **kwargs):
        folder = self.portal.bika_setup.bika_sampletypes
        if "folder" in kwargs:
            folder = kwargs.get("folder", folder)
            del kwargs["folder"]
        obj = _createObjectByType("SampleType", folder, tmpID())
        obj.edit(**kwargs)
        obj.unmarkCreationFlag()
        renameAfterCreation(obj)
        notify(ObjectInitializedEvent(obj))
        return obj

    def add_analysisrequest(self, client, kwargs, services):
        return create_analysisrequest(client, self.request, kwargs, services)

    def add_worksheet(self, ar, **kwargs):
        # Worksheet creation
        wsfolder = self.portal.worksheets
        ws = _createObjectByType("Worksheet", wsfolder, tmpID())
        ws.processForm()
        bsc = api.get_tool("senaite_catalog_setup")
        lab_contacts = [o.getObject() for o in bsc(portal_type="LabContact")]
        lab_contact = [
            o for o in lab_contacts if o.getUsername() == "analyst1"
        ]
        self.assertEquals(len(lab_contact), 1)
        lab_contact = lab_contact[0]
        ws.setAnalyst(lab_contact.getUsername())
        ws.setResultsLayout(self.portal.bika_setup.getWorksheetLayout())
        # Add analyses into the worksheet
        self.request["context_uid"] = ws.UID()
        for analysis in ar.getAnalyses():
            ws.addAnalysis(analysis.getObject())
        self.assertEquals(len(ws.getAnalyses()), 2)
        return ws

    def add_duplicate(self, worksheet, **kwargs):
        # Add a duplicate for slot 1 (there's only one slot)
        worksheet.addDuplicateAnalyses("1", None)
        ans = worksheet.getAnalyses()
        dup = [an for an in ans if an.portal_type == "DuplicateAnalysis"]
        return dup


class DataTestCase(BaseTestCase):
    """Use for test cases which rely on the demo data"""

    layer = DATA_TESTING
