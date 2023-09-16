# -*- coding: utf-8 -*-

from Products.Archetypes.public import DisplayList
from senaite.core.exportimport.dataimport import ImportView as IV
from bika.lims import api


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
