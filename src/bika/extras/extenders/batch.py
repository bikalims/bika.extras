# -*- coding: utf-8 -*-

from Products.Archetypes.Widget import BooleanWidget
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from zope.component import adapts
from zope.interface import implementer

from bika.extras.config import _
from bika.extras.interfaces import IBikaExtrasLayer
from bika.extras.extenders.fields import ExtBooleanField
from bika.lims.interfaces import IBatch


notified_samples_received_field = ExtBooleanField(
    "NotifiedSamplesReceived",
    mode="rw",
    schemata="default",
    widget=BooleanWidget(
        label=_("Notified Batch Samples have been Received"),
        format="select",
        visible={"add": "invinsible", "edit": "invinsible"},
    ),
)


@implementer(ISchemaExtender, IBrowserLayerAwareExtender)
class BatchSchemaExtender(object):
    adapts(IBatch)
    layer = IBikaExtrasLayer

    fields = [
        notified_samples_received_field,
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields
