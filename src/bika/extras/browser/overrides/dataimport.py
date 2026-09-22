# -*- coding: utf-8 -*-

import os
import json
import traceback

import transaction
from Products.Archetypes.public import DisplayList
from zope.component import getAdapters

from bika.lims import api
from bika.lims import logger
from bika.lims import senaiteMessageFactory as _
from bika.lims.interfaces import ISetupDataSetList
from senaite.core.exportimport import instruments
from senaite.core.exportimport.dataimport import ImportView as IV
from senaite.core.browser.form.adapters.data_import import EditForm as EF

from bika.extras.browser.overrides.load_setup_data import LoadSetupData


class EditForm(EF):

    def get_default_import_template(self):
        """Returns the path of the default import template
        """
        import bika.extras.browser.overrides.dataimport
        path = os.path.dirname(bika.extras.browser.overrides.dataimport.__file__)
        template = "templates/instrument.pt"
        return os.path.join(path, template)

    def handle_data_import(self):
        try:
            LoadSetupData(self.context, self.request)()
        except Exception:
            tb = traceback.format_exc()
            self.add_status_message(
                message=tb, title="Error", level="danger", flush=True)
            logger.error(tb)
            transaction.abort()
            return False
        self.add_status_message(
            message=_("Data import successful"),
            title="Info", level="success", flush=True)
        return True


class ImportView(IV):
    """
    """

    def getSetupDatas(self):
        datasets = []
        new_datasets = []
        adapters = getAdapters((self.context, ), ISetupDataSetList)
        for name, adapter in adapters:
            datasets.extend(adapter())
        for dataset in datasets:
            if dataset['projectname'] == "bika.lims":
                continue
            new_datasets.append(dataset)
        return new_datasets

    def __call__(self):
        if "submitted" not in self.request:
            return self.template()

        if ("setupfile" in self.request.form
                or "setupexisting" in self.request.form):
            return LoadSetupData(self.context, self.request)()

        interface = self.request.get("exim")
        exim = instruments.getExim(interface)
        if not exim:
            error = "Importer not found for: %s" % interface
            return json.dumps({"errors": [error], "log": "", "warns": ""})
        return exim.Import(self.context, self.request)

    def getProjectName(self):
        adapters = getAdapters((self.context, ), ISetupDataSetList)
        productnames = [name for name, adapter in adapters]
        if len(productnames) == 1:
            productnames[0] = 'bika.extras'
        return productnames[len(productnames) - 1]

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
