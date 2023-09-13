from archetypes.schemaextender.interfaces import ISchemaModifier
from zope.component import adapts
from zope.interface import implements

from bika.extras.config import _
from bika.extras.interfaces import IBikaExtrasLayer
from bika.lims.content.worksheettemplate import WorksheetTemplate


class WorksheetTemplateSchemaModifier(object):
    adapts(WorksheetTemplate)
    implements(ISchemaModifier)
    layer = IBikaExtrasLayer

    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self.fields

    def fiddle(self, schema):
        """
        """
        schema["description"].schemata = "Description"
        schema["description"].widget.visible = True
        schema["RestrictToMethod"].widget.label = "Method"
        schema["RestrictToMethod"].widget.description = _(
            "Restrict the available analysis services and instruments"
            "to those with the selected method."
            " In order to apply this change to the services list, you "
            "should save the change first."
        )
        return schema
