# -*- coding: utf-8 -*-
#
# This file is part of BIKA.EXTRAS.
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

import collections

from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.permissions import AddARTemplate
from bika.lims.controlpanel.bika_artemplates import TemplatesView as TV
from bika.lims.utils import get_link


class TemplatesView(TV):

    def __init__(self, context, request):
        super(TemplatesView, self).__init__(context, request)

        self.catalog = "senaite_catalog_setup"
        self.contentFilter = {
            "portal_type": "ARTemplate",
            "sort_on": "sortable_title",
            "sort_order": "ascending",
            "path": {
                "query": api.get_path(context),
                "level": 0},
        }

        self.context_actions = {
            _("Add"): {
                "url": "createObject?type_name=ARTemplate",
                "permission": AddARTemplate,
                "icon": "++resource++bika.lims.images/add.png"}
        }

        self.title = self.context.translate(_("Sample Templates"))
        self.icon = "{}/{}".format(
            self.portal_url,
            "/++resource++bika.lims.images/artemplate_big.png"
        )

        self.show_select_row = False
        self.show_select_column = True

        self.columns = collections.OrderedDict((
            ("Title", {
                "title": _("Title"),
                "index": "sortable_title"}),
            ("Description", {
                "title": _("Description"),
                "index": "Description",
                "toggle": True, }),
            ("SamplePointTitle", {
                "title": _("Sample Point"),
                "toggle": True, }),
            ("SampleTypeTitle", {
                "title": _("Sample Type"),
                "toggle": True, }),
            ("NumberOfPartitions", {
                "title": _("Number Of Partitions"),
                "toggle": True, }),
            ("Profile", {
                "title": _("Profile"),
                "toggle": True, }),
        ))

        self.review_states = [
            {
                "id": "default",
                "title": _("Active"),
                "contentFilter": {"is_active": True},
                "columns": self.columns.keys(),
            }, {
                "id": "inactive",
                "title": _("Inactive"),
                "contentFilter": {'is_active': False},
                "columns": self.columns.keys(),
            }, {
                "id": "all",
                "title": _("All"),
                "contentFilter": {},
                "columns": self.columns.keys(),
            },
        ]

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.
        The use of this service prevents the extra-loops in child objects.
        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        obj = api.get_object(obj)
        title = obj.Title()
        description = obj.Description()
        url = obj.absolute_url()

        item["replace"]["Title"] = get_link(url, value=title)
        item["Description"] = description
        sample_point = obj.getSamplePoint()
        item["SamplePointTitle"] = sample_point.Title() if sample_point else ""
        sample_type = obj.getSampleType()
        item["SampleTypeTitle"] = sample_type.Title() if sample_type else ""
        number_of_partitions = len(obj.getPartitions())
        item["NumberOfPartitions"] = number_of_partitions
        profile = obj.getAnalysisProfile()
        item["Profile"] = profile.Title() if profile else ""
        return item
