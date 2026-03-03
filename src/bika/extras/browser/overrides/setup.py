from senaite.core.browser.setup.edit import SetupEditView as SEV
from bika.extras import _


class SetupEditView(SEV):
    """Custom edit view for SENAITE Setup
    """

    def __init__(self, context, request):
        super(SetupEditView, self).__init__(context, request)
        self.context = context
        self.request = request

    @property
    def label(self):
        """Override to show 'SENAITE Setup' instead of 'Edit SENAITE Setup'
        """
        return _(u"BIKA Setup")
