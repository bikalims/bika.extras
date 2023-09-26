# -*- coding: utf-8 -*-

from plone import api
from plone.registry.interfaces import IRecordModifiedEvent


def restore_logo(instance, event):
    """Event handler when a new Client was created
    """
    if not event.__providedBy__(IRecordModifiedEvent):
        return

    record_name = event.record.__name__
    if record_name == "plone.site_title":
        site_title = "SENAITE LIMS"
        if event.newValue == site_title and event.oldValue != "Plone site" \
                and event.oldValue != site_title:
            api.portal.set_registry_record(record_name, event.oldValue)
            return

    if record_name == "senaite.toolbar_logo":
        senaite_logo = "/++plone++senaite.core.static/images/senaite.svg"
        site_logo = "/logo.png"
        if event.newValue == senaite_logo and event.oldValue == site_logo:
            api.portal.set_registry_record(record_name, event.oldValue)
            return

    if record_name == "senaite.toolbar_logo_styles":
        ht = "15px"
        if event.newValue["height"] == ht and event.oldValue['height'] != ht:
            api.portal.set_registry_record(record_name, event.oldValue)
            return
