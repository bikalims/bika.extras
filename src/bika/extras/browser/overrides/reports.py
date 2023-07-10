# -*- coding: utf-8 -*-

import os

from DateTime import DateTime
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import get_installer
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize import ram
from zope.component import getAdapters

from bika.extras import _
from bika.lims import api
from bika.lims.browser.reports import AdministrationView as AV
from bika.lims.browser.reports import SubmitForm as SF
from bika.lims.browser.reports.selection_macros import _cache_key_select_client
from bika.lims.browser.reports.selection_macros import \
    SelectionMacrosView as SMV
from bika.lims.interfaces import IProductivityReport
from bika.lims.utils import createPdf
from bika.lims.utils import logged_in_client
from bika.lims.utils import to_unicode as _u
from bika.lims.utils import to_utf8 as _c

from senaite.core.catalog import CLIENT_CATALOG


class SelectionMacrosView(SMV):

    @ram.cache(_cache_key_select_client)
    def select_client(self, style=None):
        client_catalog = api.get_tool(CLIENT_CATALOG)
        self.style = style
        self.clients = client_catalog(
            portal_type='Client', sort_on='sortable_title')
        return self.select_client_pt()


class AdministrationView(AV):
    """ Administration View form
    """
    template = ViewPageTemplateFile("templates/administration.pt")

    def is_senaite_crms_installed(self):
        qi = get_installer(self.portal)
        return qi.is_product_installed("senaite.crms")


class SubmitForm(SF):
    """ Redirect to specific report
    """

    def __call__(self):
        """Create and render selected report
        """

        # if there's an error, we return productivity.pt which requires these.
        self.selection_macros = SelectionMacrosView(self.context, self.request)
        self.additional_reports = []
        adapters = getAdapters((self.context, ), IProductivityReport)
        for name, adapter in adapters:
            report_dict = adapter(self.context, self.request)
            report_dict['id'] = name
            self.additional_reports.append(report_dict)

        report_id = self.request.get('report_id', '')
        if not report_id:
            message = _("No report specified in request")
            self.logger.error(message)
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.template()

        self.date = DateTime()
        username = self.context.portal_membership.getAuthenticatedMember().getUserName()
        self.reporter = self.user_fullname(username)
        self.reporter_email = self.user_email(username)

        # signature image
        self.reporter_signature = ""
        c = [x for x in self.senaite_catalog_setup(portal_type='LabContact')
             if x.getObject().getUsername() == username]
        if c:
            sf = c[0].getObject().getSignature()
            if sf:
                self.reporter_signature = sf.absolute_url() + "/Signature"

        lab = self.context.bika_setup.laboratory
        self.laboratory = lab
        self.lab_title = lab.getName()
        self.lab_address = lab.getPrintAddress()
        self.lab_email = lab.getEmailAddress()
        self.lab_url = lab.getLabURL()

        client = logged_in_client(self.context)
        if client:
            clientuid = client.UID()
            self.client_title = client.Title()
            self.client_address = client.getPrintAddress()
        else:
            clientuid = None
            self.client_title = None
            self.client_address = None

        # Render form output

        # the report can add file names to this list; they will be deleted
        # once the PDF has been generated.  temporary plot image files, etc.
        self.request['to_remove'] = []

        if "report_module" in self.request:
            module = self.request["report_module"]
        elif report_id == "administration_nearexpirereferencesamples":
            module = "senaite.crms.browser.reports.%s" % report_id
        else:
            module = "bika.lims.browser.reports.%s" % report_id
        try:
            exec ("from %s import Report" % module)
            # required during error redirect: the report must have a copy of
            # additional_reports, because it is used as a surrogate view.
            Report.additional_reports = self.additional_reports
        except ImportError:
            message = "Report %s.Report not found (shouldn't happen)" % module
            self.logger.error(message)
            self.context.plone_utils.addPortalMessage(message, 'error')
            return self.template()

        # Report must return dict with:
        # - report_title - title string for pdf/history listing
        # - report_data - rendered report
        output = Report(self.context, self.request)()

        # if CSV output is chosen, report returns None
        if not output:
            return

        if type(output) in (str, unicode, bytes):
            # remove temporary files
            for f in self.request['to_remove']:
                os.remove(f)
            return output

        # The report output gets pulled through report_frame.pt
        self.reportout = output['report_data']
        framed_output = self.frame_template()

        # this is the good part
        result = createPdf(framed_output)

        # remove temporary files
        for f in self.request['to_remove']:
            os.remove(f)

        if result:
            # Create new report object
            reportid = self.context.generateUniqueId('Report')
            report = _createObjectByType("Report", self.context, reportid)
            report.edit(Client=clientuid)
            report.processForm()

            # write pdf to report object
            report.edit(title=output['report_title'], ReportFile=result)
            report.reindexObject()

            fn = "%s - %s" % (self.date.strftime(self.date_format_short),
                              _u(output['report_title']))

            setheader = self.request.RESPONSE.setHeader
            setheader('Content-Type', 'application/pdf')
            setheader("Content-Disposition",
                      "attachment;filename=\"%s\"" % _c(fn))
            self.request.RESPONSE.write(result)

        return
