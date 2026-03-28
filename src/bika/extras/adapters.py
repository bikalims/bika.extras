# -*- coding: utf-8 -*-

from zope.interface import implements
from pkg_resources import resource_listdir
from bika.lims.interfaces import ISetupDataSetList


class SetupDataSetList:

    implements(ISetupDataSetList)

    def __init__(self, context):
        self.context = context

    def __call__(self, projectname="bika.extras"):
        datasets = []
        mapping = {
            "bika.extras": "Bika LIMS",
        }
        for f in resource_listdir(projectname, 'setupdata'):
            fn = f + ".xlsx"
            try:
                if fn in resource_listdir(projectname, 'setupdata/%s' % f):
                    data = {
                        "projectname": projectname,
                        "dataset": f,
                        "displayname": mapping.get(projectname, projectname),
                    }
                    datasets.append(data)
            except OSError:
                pass
        return datasets
