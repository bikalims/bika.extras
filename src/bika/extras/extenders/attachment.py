from archetypes.schemaextender.interfaces import ISchemaModifier
from zope.component import adapts
from zope.interface import implements

from bika.extras.interfaces import IBikaExtrasLayer
from bika.lims.content.attachment import Attachment


class AttachmentSchemaModifier(object):
    adapts(Attachment)
    implements(ISchemaModifier)
    layer = IBikaExtrasLayer

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def fiddle(self, schema):
        """
        """
        schema["RenderInReport"].default = False
        return schema
