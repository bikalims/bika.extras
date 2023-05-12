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

from DateTime import DateTime
from plone.registry.interfaces import IRegistry
from zope.component import getUtility

from bika.lims.browser.stickers import Sticker as SV
from senaite.core.api import dtime


class Sticker(SV):
    """Invoked via URL on an object or list of objects from the types
       AnalysisRequest, Sample or ReferenceSample.

       Renders a preview for the objects, a control to allow the user to
       select the sticker template to be invoked and print.

       In order to create a sticker inside an Add-on you have to create a
       directory inside the resource directory

       This defines the resource folder to look for:

       - path: addon/stickers/configure.zcml
           ...
           **Defining stickers for samples and partitions
           <plone:static
             directory="templates"
             type="stickers"
             name="ADDON stickers" />
           ...

       This is how to add general stickers for samples:

       - addon/stickers/templates/

           -- code_39_40x20mm.{css,pt}
           -- other_{sample,ar,partition}_stickers_...

       This is the way to create specific sticker for a content type.

       Note that in this case the directory '/worksheet' should contain the
       sticker templates for worksheet objects.

       - addon/stickers/templates/worksheet
           -- code_...mm.{css,pt}
           -- other_worksheet_stickers_...
    """

    def get_sticker_logo(self):
        LOGO = "/++plone++bika.coa.static/images/bikalimslogo.png"
        registry = getUtility(IRegistry)
        portal_url = self.portal_url
        try:
            logo = registry["bika.extras.sticker_logo"]
        except (AttributeError, KeyError):
            logo = LOGO
        if not logo:
            logo = LOGO
        return portal_url + logo

    def get_sticker_styles(self):
        registry = getUtility(IRegistry)
        styles = {}
        try:
            ac_style = registry["bika.extras.sticker_logo_styles"]
        except (AttributeError, KeyError):
            styles["ac_styles"] = "max-height:68px;"
        css = map(lambda ac_style: "{}:{};".format(*ac_style), ac_style.items())
        # css.append("max-width:200px;")
        styles["ac_styles"] = " ".join(css)

        try:
            logo_style = registry["bika.extras.sticker_logo_styles"]
        except (AttributeError, KeyError):
            styles["logo_styles"] = "height:15px;"
        css = map(lambda logo_style: "{}:{};".format(*logo_style), logo_style.items())
        styles["logo_styles"] = " ".join(css)
        return styles

    def get_today_now(self):
        return dtime.date_to_string(DateTime(), fmt="%H:%M:%S")
