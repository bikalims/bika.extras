# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from bika.lims.browser.widgets.referenceresultswidget import \
    ReferenceResultsView as RRV


class ReferenceResultsView(RRV):
    def folderitems(self):
        bsc = getToolByName(self.context, "senaite_catalog_setup")
        self.an_cats = bsc(portal_type="AnalysisCategory",
                           sort_on="sortable_title")
        self.an_cats_order = dict(
            [(b.Title, "{:04}".format(a)) for a, b in enumerate(self.an_cats)]
        )

        items = super(ReferenceResultsView, self).folderitems()
        if self.show_categories_enabled():
            self.categories = map(
                lambda x: x[0], sorted(self.categories, key=lambda x: x[1])
            )
        else:
            self.categories.sort()
        return items

    def folderitem(self, obj, item, index):
        """Service triggered each time an item is iterated in folderitems.

        The use of this service prevents the extra-loops in child objects.

        :obj: the instance of the class to be foldered
        :item: dict containing the properties of the object to be used by
            the template
        :index: current index of the item
        """
        # ensure we have an object and not a brain
        obj = api.get_object(obj)
        uid = api.get_uid(obj)
        url = api.get_url(obj)
        title = api.get_title(obj)
        cat = obj.getCategoryTitle()
        cat_order = self.an_cats_order.get(cat)

        # get the category
        if self.show_categories_enabled():
            category = obj.getCategoryTitle()
            if (category, cat_order) not in self.categories:
                self.categories.append((category, cat_order))
            item["category"] = category

        rr = self.referenceresults.get(uid, {})
        item["Title"] = title
        item["replace"]["Title"] = get_link(url, value=title)
        item["allow_edit"] = self.get_editable_columns()
        item["required"] = self.get_required_columns()
        item["selected"] = rr and True or False
        item["result"] = rr.get("result", "")
        item["min"] = rr.get("min", "")
        item["max"] = rr.get("max", "")
        item["error"] = rr.get("error", "")

        # Icons
        after_icons = ""
        if obj.getAccredited():
            after_icons += get_image("accredited.png", title=_("Accredited"))
        if obj.getAttachmentRequired():
            after_icons += get_image("attach_reqd.png", title=_("Attachment required"))
        if after_icons:
            item["after"]["Title"] = after_icons

        return item
