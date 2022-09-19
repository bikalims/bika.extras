# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import (
    applyProfile,
    FunctionalTesting,
    IntegrationTesting,
    PloneSandboxLayer,
)
from plone.testing import z2

import bika.extras


class BikaExtrasLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=bika.extras)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'bika.extras:default')


BIKA_EXTRAS_FIXTURE = BikaExtrasLayer()


BIKA_EXTRAS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(BIKA_EXTRAS_FIXTURE,),
    name='BikaExtrasLayer:IntegrationTesting',
)


BIKA_EXTRAS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(BIKA_EXTRAS_FIXTURE,),
    name='BikaExtrasLayer:FunctionalTesting',
)


BIKA_EXTRAS_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        BIKA_EXTRAS_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='BikaExtrasLayer:AcceptanceTesting',
)
