# -*- coding: utf-8 -*-
# override

import cgi
import copy
import json
import math
from decimal import Decimal
from six import string_types

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims import deprecated
from bika.lims import logger
from bika.lims.browser.fields import HistoryAwareReferenceField
from bika.lims.browser.fields import InterimFieldsField
from bika.lims.browser.fields import ResultRangeField
from bika.lims.browser.fields import UIDReferenceField
from bika.lims.browser.fields.uidreferencefield import get_backreferences
from bika.lims.browser.widgets import RecordsWidget
from bika.lims.config import LDL
from bika.lims.config import UDL
from bika.lims.content.abstractbaseanalysis import AbstractBaseAnalysis
from bika.lims.content.abstractbaseanalysis import schema
from bika.lims.interfaces import IDuplicateAnalysis
from senaite.core.permissions import FieldEditAnalysisResult
from senaite.core.permissions import ViewResults
from bika.lims.utils import formatDecimalMark
from bika.lims.utils.analysis import format_numeric_result
from bika.lims.utils.analysis import get_significant_digits
from bika.lims.workflow import getTransitionActor
from bika.lims.workflow import getTransitionDate
from DateTime import DateTime
from senaite.core.browser.fields.datetime import DateTimeField
from Products.Archetypes.Field import IntegerField
from Products.Archetypes.Field import StringField
from Products.Archetypes.references import HoldingReference
from Products.Archetypes.Schema import Schema
from Products.CMFCore.permissions import View

security = ClassSecurityInfo()


@security.public
def getEarliness(self):
    """The remaining time in minutes for this analysis to be completed.
    Returns zero if the analysis is neither 'ready to process' nor a
    turnaround time is set.
        earliness = duration - max_turnaround_time
    The analysis is late if the earliness is negative
    :return: the remaining time in minutes before the analysis reaches TAT
    :rtype: int
    """
    maxtime = self.getMaxTimeAllowed()
    is_zero_or_none = ("0", 0, None)
    if not maxtime:
        # No Turnaround time is set for this analysis
        return 0
    if (
        maxtime.get("hours") in is_zero_or_none
        and maxtime.get("minutes") in is_zero_or_none
        and maxtime.get("days") in is_zero_or_none
    ):
        return 0
    return api.to_minutes(**maxtime) - self.getDuration()
