# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.INSTRUMENTS
#
# Copyright 2018 by it's authors.


from datetime import datetime
from os.path import abspath
from os.path import dirname

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

from bika.extras.tests.base import BaseTestCase


TITLE = "BIKA EXTRAS INITIAL TEST"

here = abspath(dirname(__file__))


class TestSoftware(BaseTestCase):
    def setUp(self):
        super(TestSoftware, self).setUp()
        setRoles(self.portal, TEST_USER_ID, ["Member", "LabManager"])
        login(self.portal, TEST_USER_NAME)

        self.client = self.add_client(title="Happy Hills", ClientID="HH")

        self.contact = self.add_contact(
            self.client, Firstname="Rita", Surname="Mohale"
        )

        self.services = [
            self.add_analysisservice(
                title="Bromide",
                Keyword="Br",
                PointOfCapture="lab",
                Category=self.add_analysiscategory(
                    title="Phyisical Properties"
                ),
                AllowManualUncertainty="True",
            ),
            self.add_analysisservice(
                title="Silica",
                Keyword="SiO",
                PointOfCapture="lab",
                Category=self.add_analysiscategory(
                    title="Phyisical Properties"
                ),
                AllowManualUncertainty="True",
            ),
            self.add_analysisservice(
                title="Sulfate",
                Keyword="SO",
                PointOfCapture="lab",
                Category=self.add_analysiscategory(
                    title="Phyisical Properties"
                ),
                AllowManualUncertainty="True",
            ),
            self.add_analysisservice(
                title="Calcium",
                Keyword="Ca",
                PointOfCapture="lab",
                Category=self.add_analysiscategory(
                    title="Phyisical Properties"
                ),
                AllowManualUncertainty="True",
            ),
            self.add_analysisservice(
                title="Magnesium",
                Keyword="Mg",
                PointOfCapture="lab",
                Category=self.add_analysiscategory(
                    title="Phyisical Properties"
                ),
                AllowManualUncertainty="True",
            ),
            self.add_analysisservice(
                title="Chloride",
                Keyword="Cl",
                PointOfCapture="lab",
                Category=self.add_analysiscategory(title="Organic"),
                AllowManualUncertainty="True",
            ),
        ]
        self.sampletype = self.add_sampletype(
            title="Dust",
            RetentionPeriod=dict(days=1),
            MinimumVolume="1 kg",
            Prefix="DU",
        )

    def test_add_analysis_request(self):
        ar = self.add_analysisrequest(
            self.client,
            dict(
                Client=self.client.UID(),
                Contact=self.contact.UID(),
                DateSampled=datetime.now().date().isoformat(),
                SampleType=self.sampletype.UID(),
            ),
            [srv.UID() for srv in self.services],
        )

        self.assertEqual(ar.getClientTitle(), "Happy Hills")
