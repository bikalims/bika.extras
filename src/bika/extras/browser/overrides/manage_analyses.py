# -*- coding: utf-8 -*-

from Products.CMFCore.utils import getToolByName
from plone.memoize import view

from bika.lims import api
from bika.lims.browser.analysisrequest.manage_analyses import \
    AnalysisRequestAnalysesView as ARAV
from bika.lims.browser.analysisrequest.manage_analyses import DETACHED_STATES
from bika.lims.content.analysisspec import ResultsRangeDict
from bika.lims.interfaces import ISubmitted
from bika.lims.utils import get_image
from bika.lims.utils import get_link
from senaite.core.i18n import translate as t

from bika.extras.config import _


class AnalysisRequestAnalysesView(ARAV):
    @view.memoize
    def show_categories_enabled(self):
        """Check in the setup if categories are enabled
        """
        bika_setup = api.get_bika_setup()
        return bika_setup.getCategoriseAnalysisServices()

    def folderitems(self):
        bsc = getToolByName(self.context, "senaite_catalog_setup")
        self.an_cats = bsc(portal_type="AnalysisCategory",
                           sort_on="sortable_title")
        self.an_cats_order = dict(
            [(b.Title, "{:04}".format(a)) for a, b in enumerate(self.an_cats)]
        )

        items = super(AnalysisRequestAnalysesView, self).folderitems()
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
        cat = obj.getCategoryTitle()
        cat_order = self.an_cats_order.get(cat)

        # get the category
        if self.show_categories_enabled():
            category = obj.getCategoryTitle()
            if (category, cat_order) not in self.categories:
                self.categories.append((category, cat_order))
            item["category"] = category

        # settings for this analysis
        service_settings = self.context.getAnalysisServiceSettings(uid)
        hidden = service_settings.get("hidden", obj.getHidden())

        price = obj.getPrice()
        keyword = obj.getKeyword()

        if uid in self.analyses:
            analysis = self.analyses[uid]
            review_state = api.get_review_status(analysis)
            if review_state not in DETACHED_STATES:
                # Might differ from the service keyword
                keyword = analysis.getKeyword()
                # Mark the row as disabled if the analysis has been submitted
                item["disabled"] = ISubmitted.providedBy(analysis)
                # get the hidden status of the analysis
                hidden = analysis.getHidden()
                # get the price of the analysis
                price = analysis.getPrice()
                item["selected"] = True

        # get the specification of this object
        rr = self.get_results_range()
        spec = rr.get(keyword, ResultsRangeDict())

        item["Title"] = obj.Title()
        item["ResultUnit"] = obj.getUnit()
        item["Price"] = price
        item["before"]["Price"] = self.get_currency_symbol()
        item["allow_edit"] = self.get_editable_columns(obj)
        item["min"] = str(spec.get("min", ""))
        item["max"] = str(spec.get("max", ""))
        item["warn_min"] = str(spec.get("warn_min", ""))
        item["warn_max"] = str(spec.get("warn_max", ""))
        item["Hidden"] = hidden

        # Append info link before the service
        # see: bika.lims.site.coffee for the attached event handler
        item["before"]["Title"] = get_link(
            "analysisservice_info?service_uid={}".format(uid),
            value="<i class='fas fa-info-circle'></i>",
            css_class="overlay_panel")

        # Icons
        after_icons = ""
        if obj.getAccredited():
            after_icons += get_image(
                "accredited.png", title=t(_("Accredited")))
        if obj.getAttachmentRequired():
            after_icons += get_image(
                "attach_reqd.png", title=t(_("Attachment required")))
        if after_icons:
            item["after"]["Title"] = after_icons

        return item
