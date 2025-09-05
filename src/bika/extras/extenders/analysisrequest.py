# -*- coding: utf-8 -*-

from Products.CMFCore.permissions import View
from archetypes.schemaextender.interfaces import IBrowserLayerAwareExtender
from archetypes.schemaextender.interfaces import ISchemaExtender
from zope.component import adapts
from zope.interface import implementer

from .fields import ExtUIDReferenceField
from bika.lims.interfaces import IAnalysisRequest
from senaite.core.permissions import FieldEditBatch
from bika.extras import _
from bika.extras.interfaces import IBikaExtrasLayer
from senaite.core.browser.widgets import ReferenceWidget

sample_matrix_field = ExtUIDReferenceField(
    'SampleMatrix',
    required=0,
    allowed_types=('SampleMatrix',),
    mode="rw",
    write_permission=FieldEditBatch,
    read_permission=View,
    widget=ReferenceWidget(
        label=_("Sample Matrix"),
        render_own_label=True,
        visible={
            'add': 'edit',
            'secondary': 'disabled',
        },
        catalog_name='senaite_catalog_setup',
        base_query={"is_active": True,
                    "sort_on": "sortable_title",
                    "sort_order": "ascending"},
        showOn=True,
    ),
)


@implementer(ISchemaExtender, IBrowserLayerAwareExtender)
class AnalysisRequestSchemaExtender(object):
    adapts(IAnalysisRequest)
    layer = IBikaExtrasLayer

    fields = [
        sample_matrix_field,
    ]

    def __init__(self, context):
        self.context = context

    def getOrder(self, schematas):
        return schematas

    def getFields(self):
        return self.fields
