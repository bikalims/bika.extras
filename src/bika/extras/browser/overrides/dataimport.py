# -*- coding: utf-8 -*-

import os
from Products.Archetypes.public import DisplayList
from senaite.core.exportimport.dataimport import ImportView as IV
from senaite.core.browser.form.adapters.data_import import EditForm as EF
from bika.lims import api


class EditForm(EF):

    def get_default_import_template(self):
        """Returns the path of the default import template
        """
        import bika.extras.browser.overrides.dataimport
        path = os.path.dirname(bika.extras.browser.overrides.dataimport.__file__)
        template = "templates/instrument.pt"
        return os.path.join(path, template)


class ImportView(IV):
    """
    """

    def getInstruments(self):
        bsc = api.get_tool('senaite_catalog_setup')
        brains = bsc(portal_type='Instrument', is_active=True)
        items = [('', '...Choose an Instrument...')]
        for item in brains:
            instrument = item.getObject()
            import_interface = instrument.getImportDataInterface()
            if len(import_interface) > 1:
                items.append((item.UID, item.Title))
        items.sort(lambda x, y: cmp(x[1].lower(), y[1].lower()))
        return DisplayList(list(items))
