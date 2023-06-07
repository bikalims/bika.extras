# -*- coding: utf-8 -*-

from bika.extras import _
from bika.extras import logger

from bika.lims import api
from bika.lims.interfaces.analysis import IRequestAnalysis
from senaite.core.browser.attachment.attachment import AttachmentsView as AT


class AttachmentsView(AT):
    def action_add_to_ws(self):
        """Form action to add a new attachment in a worksheet
        """

        ws = self.context
        form = self.request.form
        attachment_file = form.get("AttachmentFile_file", None)
        service_uid = self.request.get("Service", None)
        analysis_uid = form.get("Analysis", None)
        attachment_type = form.get("AttachmentType", "")
        attachment_keys = form.get("AttachmentKeys", "")
        render_in_report = form.get("RenderInReport", False)

        # nothing to do if the attachment file is missing
        if attachment_file is None:
            logger.warn("AttachmentView.action_add_attachment: "
                        "Attachment file is missing")
            return

        if analysis_uid:
            rc = api.get_tool("reference_catalog")
            analysis = rc.lookupObject(analysis_uid)

            # create attachment
            attachment = self.create_attachment(
                ws,
                attachment_file,
                AttachmentType=attachment_type,
                AttachmentKeys=attachment_keys,
                RenderInReport=render_in_report)

            others = analysis.getAttachment()
            attachments = []
            for other in others:
                attachments.append(other.UID())
            attachments.append(attachment.UID())
            analysis.setAttachment(attachments)
            title = api.safe_unicode(api.get_title(analysis))
            self.add_status_message(
                _(u"Attachment added to analysis '{}'".format(title)))

        if service_uid:
            attached = 0
            service = api.get_object_by_uid(service_uid)

            for analysis in self.context.getAnalyses():
                if not IRequestAnalysis.providedBy(analysis):
                    continue
                if not self.is_editable(analysis):
                    continue
                if analysis.getKeyword() != service.getKeyword():
                    continue

                # create attachment
                attachment = self.create_attachment(
                    ws,
                    attachment_file,
                    AttachmentType=attachment_type,
                    AttachmentKeys=attachment_keys,
                    RenderInReport=render_in_report)

                others = analysis.getAttachment()
                attachments = []
                for other in others:
                    attachments.append(other.UID())
                attachments.append(attachment.UID())
                analysis.setAttachment(attachments)
                attached += 1

            service_title = api.safe_unicode(api.get_title(service))
            if attached > 0:
                self.add_status_message(
                    _(u"Attachment added to all '{}' analyses"
                      .format(service_title)))
            else:
                self.add_status_message(
                    _(u"No analysis found for service '{}'"
                      .format(service_title)), level="warning")

        if not any([analysis_uid, service_uid]):
            self.add_status_message(
                _("Please select an analysis or service for the attachment"),
                level="warning")

        return self.request.response.redirect(self.get_redirect_url())
