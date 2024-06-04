# -*- coding: utf-8 -*-
# override

import copy
from collections import OrderedDict
from datetime import timedelta

from AccessControl import ClassSecurityInfo
from bika.lims import api
from bika.lims import bikaMessageFactory as _
from bika.lims.browser.widgets import DecimalWidget
from bika.lims.content.abstractanalysis import AbstractAnalysis
from bika.lims.content.abstractanalysis import schema
from bika.lims.content.attachment import Attachment
from bika.lims.content.clientawaremixin import ClientAwareMixin
from bika.lims.interfaces import IAnalysis
from bika.lims.interfaces import ICancellable
from bika.lims.interfaces import IDynamicResultsRange
from bika.lims.interfaces import IInternalUse
from bika.lims.interfaces import IRoutineAnalysis
from bika.lims.interfaces.analysis import IRequestAnalysis
from bika.lims.workflow import getTransitionDate
from Products.Archetypes.Field import BooleanField
from Products.Archetypes.Field import StringField
from Products.Archetypes.Schema import Schema
from Products.ATContentTypes.utils import DT2dt
from Products.ATContentTypes.utils import dt2DT
from Products.CMFCore.permissions import View
from senaite.core.catalog.indexer.baseanalysis import sortable_title
from zope.interface import alsoProvides
from zope.interface import implements
from zope.interface import noLongerProvides

security = ClassSecurityInfo()


@security.public
def getDueDate(self):
    """Used to populate getDueDate index and metadata.
    This calculates the difference between the time the analysis processing
    started and the maximum turnaround time. If the analysis has no
    turnaround time set or is not yet ready for proces, returns None
    """
    tat = self.getMaxTimeAllowed()
    is_zero_or_none = ("0", 0, None)
    if not tat:
        return None
    if (
        tat.get("hours") in is_zero_or_none
        and tat.get("minutes") in is_zero_or_none
        and tat.get("days") in is_zero_or_none
    ):
        return None
    start = self.getStartProcessDate()
    if not start:
        return None

    # delta time when the first analysis is considered as late
    delta = timedelta(minutes=api.to_minutes(**tat))

    # calculated due date
    end = dt2DT(DT2dt(start) + delta)

    # delta is within one day, return immediately
    if delta.days == 0:
        return end

    # get the laboratory workdays
    setup = api.get_setup()
    workdays = setup.getWorkdays()

    # every day is a workday, no need for calculation
    if workdays == tuple(map(str, range(7))):
        return end

    # reset the due date to the received date, and add only for configured
    # workdays another day
    due_date = end - delta.days

    days = 0
    while days < delta.days:
        # add one day to the new due date
        due_date += 1
        # skip if the weekday is a non working day
        if str(due_date.asdatetime().weekday()) not in workdays:
            continue
        days += 1

    return due_date
