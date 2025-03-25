# -*- coding: utf-8 -*-

from bika.lims import api
from bika.extras.config import _
from bika.lims.utils import format_supsub
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from senaite.core.browser.widgets.services_widget import ServicesWidget as SW
from Products.CMFCore.utils import getToolByName


class ServicesWidget(SW):
    """Listing widget for Analysis Services
    """

    def folderitems(self):
        """Sort by Categories
        """

        bsc = getToolByName(self.context, "senaite_catalog_setup")
        self.an_cats = bsc(
            portal_type="AnalysisCategory",
            sort_on="sortable_title")
        self.an_cats_order = dict([
            (b.Title, "{:04}".format(a))
            for a, b in enumerate(self.an_cats)])

        items = super(ServicesWidget, self).folderitems()

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
        keyword = obj.getKeyword()
        cat = obj.getCategoryTitle()
        cat_order = self.an_cats_order.get(cat)

        # get the category
        if self.show_categories_enabled():
            category = obj.getCategoryTitle()
            if (category, cat_order) not in self.categories:
                self.categories.append((category, cat_order))
            item["category"] = category

        hidden = False
        # get the hidden setting from the records
        if self.records.get(uid):
            record = self.records.get(uid, {}) or {}
            hidden = record.get("hidden", False)
        else:
            # get the default value from the service
            hidden = obj.getHidden()

        item["replace"]["Title"] = get_link(url, value=title)
        item["Price"] = self.format_price(obj.Price)
        item["allow_edit"] = self.get_editable_columns()
        item["selected"] = False
        item["Hidden"] = hidden
        item["replace"]["Hidden"] = _("Yes") if hidden else _("No")
        item["selected"] = uid in self.records
        item["Keyword"] = keyword
        item["replace"]["Keyword"] = "<code>{}</code>".format(keyword)

        # Add methods
        methods = obj.getMethods()
        if methods:
            links = map(
                lambda m: get_link(
                    m.absolute_url(), value=m.Title(), css_class="link"),
                methods)
            item["replace"]["Methods"] = ", ".join(links)
        else:
            item["methods"] = ""

        # Unit
        unit = obj.getUnit()
        item["Unit"] = unit or ""
        item["replace"]["Unit"] = unit and format_supsub(unit) or ""

        # Icons
        after_icons = ""
        if obj.getAccredited():
            after_icons += get_image(
                "accredited.png", title=_("Accredited"))
        if obj.getAttachmentRequired():
            after_icons += get_image(
                "attach_reqd.png", title=_("Attachment required"))
        if after_icons:
            item["after"]["Title"] = after_icons

        return item
