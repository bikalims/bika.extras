# -*- coding: utf-8 -*-

from plone import api
from plone.registry.interfaces import IRecordModifiedEvent


def restore_logo(instance, event):
    """Preserve site branding when profiles reset registry defaults."""
    if not IRecordModifiedEvent.providedBy(event):
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
        # Theme and custom logo paths must survive core registry imports.
        if (event.newValue == senaite_logo and event.oldValue
                and event.oldValue != senaite_logo):
            api.portal.set_registry_record(record_name, event.oldValue)
            return

    if record_name == "senaite.toolbar_logo_styles":
        ht = "15px"
        if event.newValue["height"] == ht and event.oldValue['height'] != ht:
            api.portal.set_registry_record(record_name, event.oldValue)
            return
