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
import six
from archetypes.schemaextender.interfaces import IExtensionField
from Products.Archetypes import public
from senaite.core.browser.fields.datetime import DateTimeField
from senaite.core.browser.fields.record import RecordField
from senaite.core.browser.fields.records import RecordsField
from bika.lims.browser.fields import UIDReferenceField
from zope.interface import implements
from zope.site.hooks import getSite


class ExtensionField(object):
    """Mix-in class to make Archetypes fields not depend on generated
    accessors and mutators, and use AnnotationStorage by default.
    """

    implements(IExtensionField)
    storage = public.AnnotationStorage()

    def __init__(self, *args, **kwargs):
        super(ExtensionField, self).__init__(*args, **kwargs)
        self.args = args
        self.kwargs = kwargs

    def getAccessor(self, instance):
        def accessor():
            if self.getType().endswith("ReferenceField"):
                return self.get(instance.__of__(getSite()))
            else:
                return self.get(instance)

        return accessor

    def getEditAccessor(self, instance):
        def edit_accessor():
            if self.getType().endswith("ReferenceField"):
                return self.getRaw(instance.__of__(getSite()))
            else:
                return self.getRaw(instance)

        return edit_accessor

    def getMutator(self, instance):
        def mutator(value, **kw):
            if self.getType().endswith("ReferenceField"):
                self.set(instance.__of__(getSite()), value)
            else:
                self.set(instance, value)

        return mutator

    def getIndexAccessor(self, instance):
        name = getattr(self, "index_method", None)
        if name is None or name == "_at_accessor":
            return self.getAccessor(instance)
        elif name == "_at_edit_accessor":
            return self.getEditAccessor(instance)
        elif not isinstance(name, six.string_types):
            raise ValueError("Bad index accessor value: %r", name)
        else:
            return getattr(instance, name)


class ExtBooleanField(ExtensionField, public.BooleanField):
    "Field extender"


class ExtComputedField(ExtensionField, public.ComputedField):
    "Field extender"


class ExtDateTimeField(ExtensionField, DateTimeField):
    "Field extender"


class ExtFloatField(ExtensionField, public.FloatField):
    "Field extender"


class ExtIntegerField(ExtensionField, public.IntegerField):
    "Field extender"


class ExtLinesField(ExtensionField, public.LinesField):
    "Field extender"


class ExtRecordField(ExtensionField, RecordField):
    "Field extender"


class ExtRecordsField(ExtensionField, RecordsField):
    "Field extender"


class ExtReferenceField(ExtensionField, public.ReferenceField):
    "Field extender"


class ExtStringField(ExtensionField, public.StringField):
    "Field extender"


class ExtTextField(ExtensionField, public.TextField):
    "Field extender"

class ExtUIDReferenceField(ExtensionField, UIDReferenceField):
    "Field extender"