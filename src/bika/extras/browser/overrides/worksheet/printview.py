# -*- coding: utf-8 -*-

import os
import glob
import traceback
from plone.resource.utils import iterDirectoriesOfType
from plone.resource.utils import queryResourceDirectory
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from bika.lims.browser.worksheet.views.printview import PrintView as PV
from bika.extras import _


class PrintView(PV):
    """Print view for a worksheet. This view acts as a placeholder, so
    the user can select the preferred options (AR by columns, AR by
    rows, etc.) for printing. Both a print button and pdf button
    are shown.
    """

    template = ViewPageTemplateFile("templates/print.pt")
    _TEMPLATES_DIR = "templates/print"
    # Add-on folder to look for templates
    _TEMPLATES_ADDON_DIR = "worksheets"

    def getCSS(self):
        """Returns the css style to be used for the current template.
        If the selected template is 'default.pt', this method will
        return the content from 'default.css'. If no css file found
        for the current template, returns empty string
        """
        template = self.request.get("template", self._DEFAULT_TEMPLATE)
        content = ""
        if template.find(":") >= 0:
            prefix, template = template.split(":")
            resource = queryResourceDirectory(
                self._TEMPLATES_ADDON_DIR, prefix
            )
            css = "{0}.css".format(template[:-3])
            if css in resource.listDirectory():
                content = resource.readFile(css)
        else:
            this_dir = os.path.dirname(os.path.abspath(__file__))
            templates_dir = os.path.join(this_dir, self._TEMPLATES_DIR)
            path = "%s/%s.css" % (templates_dir, template[:-3])
            with open(path, "r") as content_file:
                content = content_file.read()
        return content

    def getWSTemplates(self):
        """Returns a DisplayList with the available templates found in
        templates/worksheets
        """
        this_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(this_dir, self._TEMPLATES_DIR)
        tempath = "%s/%s" % (templates_dir, "*.pt")
        templates = [t.split("/")[-1] for t in glob.glob(tempath)]
        out = []
        for template in templates:
            out.append({"id": template, "title": template[:-3]})
        for templates_resource in iterDirectoriesOfType(
            self._TEMPLATES_ADDON_DIR
        ):
            prefix = templates_resource.__name__
            templates = [
                tpl
                for tpl in templates_resource.listDirectory()
                if tpl.endswith(".pt")
            ]
            for template in templates:
                out.append(
                    {
                        "id": "{0}:{1}".format(prefix, template),
                        "title": "{0} ({1})".format(template[:-3], prefix),
                    }
                )
        return out

    def renderWSTemplate(self):
        """Returns the current worksheet rendered with the template
        specified in the request (param 'template').
        Moves the iterator to the next worksheet available.
        """
        templates_dir = self._TEMPLATES_DIR
        embedt = self.request.get("template", self._DEFAULT_TEMPLATE)
        if embedt.find(":") >= 0:
            prefix, embedt = embedt.split(":")
            templates_dir = queryResourceDirectory(
                self._TEMPLATES_ADDON_DIR, prefix
            ).directory
        embed = ViewPageTemplateFile(os.path.join(templates_dir, embedt))
        reptemplate = ""
        try:
            reptemplate = embed(self)
        except Exception:
            tbex = traceback.format_exc()
            wsid = self._worksheets[self._current_ws_index].id
            reptemplate = (
                "<div class='error-print'>%s - %s '%s':<pre>%s</pre></div>"
                % (wsid, _("Unable to load the template"), embedt, tbex)
            )
        if self._current_ws_index < len(self._worksheets):
            self._current_ws_index += 1
        return reptemplate
