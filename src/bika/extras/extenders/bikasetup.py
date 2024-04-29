# -*- coding: utf-8 -*-

from Products.Archetypes.Widget import BooleanWidget
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from zope.component import adapts
from zope.interface import implementer

from bika.extras.config import _
from bika.extras.extenders.fields import ExtBooleanField
from bika.extras.interfaces import IBikaExtrasLayer
from bika.lims.interfaces import IBikaSetup

worksheet_tite_field = ExtBooleanField(
    "WorksheetTitle",
    mode="rw",
    schemata="Analyses",
    default=False,
    widget=BooleanWidget(
        label=_(
            "label_bikasetup_worksheet_title",
            "Worksheet Title",
        ),
        description=_(
            "description_bikasetup_worksheet_title",
            default="Use analysis category to give titles for Worksheets"
        ),
    ),
)


@implementer(ISchemaExtender, IBrowserLayerAwareExtender)
class BikaSetupSchemaExtender(object):
    adapts(IBikaSetup)
    layer = IBikaExtrasLayer

    fields = [
        worksheet_tite_field,
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields
