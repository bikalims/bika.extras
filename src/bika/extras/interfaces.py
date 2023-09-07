# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.publisher.interfaces.browser import IDefaultBrowserLayer
from bika.lims.interfaces import IBikaLIMS


class IBikaExtrasLayer(IBikaLIMS):
    """Marker interface that defines a Zope 3 browser layer.
    """


class IBikaExtrasBrowserLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""
