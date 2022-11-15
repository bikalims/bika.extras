# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.CORE.
#
# SENAITE.CORE is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2021 by it's authors.
# Some rights reserved, see README and LICENSE.


from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from zope.event import notify

from bika.lims.utils import tmpID
from bika.lims.idserver import renameAfterCreation
from senaite.core.exportimport.setupdata import WorksheetImporter


class Analysis_Specifications(WorksheetImporter):

    def resolve_service(self, row):
        bsc = getToolByName(self.context, "senaite_catalog_setup")
        service = bsc(
            portal_type="AnalysisService",
            title=safe_unicode(row["service"])
        )
        if not service:
            service = bsc(
                portal_type="AnalysisService",
                getKeyword=safe_unicode(row["service"])
            )
        service = service[0].getObject()
        return service

    def Import(self):
        bucket = {}
        pc = getToolByName(self.context, "portal_catalog")
        bsc = getToolByName(self.context, "senaite_catalog_setup")
        # collect up all values into the bucket
        for row in self.get_rows(3):
            title = row.get("Title", False)
            if not title:
                title = row.get("title", False)
                if not title:
                    continue
            parent = row["Client_title"] if row["Client_title"] else "lab"
            st = row["SampleType_title"] if row["SampleType_title"] else ""
            description = row["Description"] if row["Description"] else ""
            service = self.resolve_service(row)

            if parent not in bucket:
                bucket[parent] = {}
            if title not in bucket[parent]:
                bucket[parent][title] = {"sampletype": st, "resultsrange": []}
                bucket[parent][title]["description"] = description
            bucket[parent][title]["resultsrange"].append({
                "keyword": service.getKeyword(),
                "min": row["min"] if row["min"] else "0",
                "max": row["max"] if row["max"] else "0",
            })
        # write objects.
        for parent in bucket.keys():
            for title in bucket[parent]:
                if parent == "lab":
                    folder = self.context.bika_setup.bika_analysisspecs
                else:
                    proxy = pc(portal_type="Client", getName=safe_unicode(parent))[0]
                    folder = proxy.getObject()
                st = bucket[parent][title]["sampletype"]
                resultsrange = bucket[parent][title]["resultsrange"]
                description = bucket[parent][title]["description"]
                if st:
                    st_uid = bsc(portal_type="SampleType", title=safe_unicode(st))[0].UID
                obj = _createObjectByType("AnalysisSpec", folder, tmpID())
                obj.edit(title=title)
                obj.edit(description=description)
                obj.setResultsRange(resultsrange)
                if st:
                    obj.setSampleType(st_uid)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))
