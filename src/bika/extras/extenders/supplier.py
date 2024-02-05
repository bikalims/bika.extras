# -*- coding: utf-8 -*-

from Products.Archetypes.Widget import StringWidget
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import ISchemaModifier
from archetypes.schemaextender.interfaces import ISchemaExtender
from zope.interface import implements
from zope.component import adapts
from zope.interface import implementer

from bika.extras import _
from bika.extras import is_installed
from bika.extras.extenders.fields import ExtStringField
from bika.extras.interfaces import IBikaExtrasLayer
from bika.lims.interfaces import ISupplier


lab_account_number = ExtStringField(
    "LabAccountNumber",
    mode="rw",
    widget=StringWidget(
        label=_(u"Lab Account Number"),
        description=_("Lab's account number with a Supplier"),
    ),
)


@implementer(ISchemaExtender, IBrowserLayerAwareExtender)
class SupplierSchemaExtender(object):
    adapts(ISupplier)
    layer = IBikaExtrasLayer

    fields = [
        lab_account_number,
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields


class SupplierSchemaModifier(object):
    adapts(ISupplier)
    implements(ISchemaModifier)
    layer = IBikaExtrasLayer

    def __init__(self, context):
        self.context = context

    def fiddle(self, schema):
        """
        """
        if is_installed():
            schema['Website'].widget.label = "Website"
            schema['SWIFTcode'].widget.label = "SWIFT code"
            schema.moveField('LabAccountNumber', before='TaxNumber')

        return schema
