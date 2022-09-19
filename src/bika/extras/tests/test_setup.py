# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from bika.extras.testing import BIKA_EXTRAS_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles, TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that bika.extras is properly installed."""

    layer = BIKA_EXTRAS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if bika.extras is installed."""
        self.assertTrue(self.installer.isProductInstalled(
            'bika.extras'))

    def test_browserlayer(self):
        """Test that IBikaExtrasLayer is registered."""
        from bika.extras.interfaces import (
            IBikaExtrasLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IBikaExtrasLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = BIKA_EXTRAS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstallProducts(['bika.extras'])
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if bika.extras is cleanly uninstalled."""
        self.assertFalse(self.installer.isProductInstalled(
            'bika.extras'))

    def test_browserlayer_removed(self):
        """Test that IBikaExtrasLayer is removed."""
        from bika.extras.interfaces import \
            IBikaExtrasLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IBikaExtrasLayer,
            utils.registered_layers())
