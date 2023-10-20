BIKA EXTRAS
===================

Import and export instrument adapters for SENAITE

Running this test from the buildout directory::

    bin/test test_doctests -t EXTRAS


Test Setup
----------
Needed imports::

    >>> import os
    >>> import cStringIO
    >>> from bika.lims import api
    >>> from bika.lims.utils.analysisrequest import create_analysisrequest
    >>> from DateTime import DateTime

    >>> from senaite.app.supermodel.interfaces import ISuperModel
    >>> from bika.extras.tests import test_setup
    >>> from zope.component import getAdapter
    >>> from zope.publisher.browser import FileUpload, TestRequest

Functional helpers::

    >>> def timestamp(format="%Y-%m-%d"):
    ...     return DateTime().strftime(format)

    >>> class TestFile(object):
    ...     def __init__(self, file, filename='dummy.txt'):
    ...         self.file = file
    ...         self.headers = {}
    ...         self.filename = filename

Variables::

    >>> date_now = timestamp()
    >>> portal = self.portal
    >>> request = self.request
    >>> bika_setup = portal.bika_setup
    >>> bika_sampletypes = bika_setup.bika_sampletypes
    >>> bika_samplepoints = bika_setup.bika_samplepoints
    >>> bika_analysiscategories = bika_setup.bika_analysiscategories
    >>> bika_analysisservices = bika_setup.bika_analysisservices
    >>> bika_calculations = bika_setup.bika_calculations
    >>> bika_methods = portal.methods

We need certain permissions to create and access objects used in this test,
so here we will assume the role of Lab Manager::

    >>> from plone.app.testing import TEST_USER_ID
    >>> from plone.app.testing import setRoles
    >>> setRoles(portal, TEST_USER_ID, ['Manager',])


Import test
-----------

Required steps: Create and receive Analysis Request for import test
...................................................................

An `AnalysisRequest` can only be created inside a `Client`, and it also requires a `Contact` and
a `SampleType`::

    >>> clients = self.portal.clients
    >>> client = api.create(clients, "Client", Name="NARALABS", ClientID="NLABS")
    >>> client
    <Client at /plone/clients/client-1>
    >>> contact = api.create(client, "Contact", Firstname="Juan", Surname="Gallostra")
    >>> contact
    <Contact at /plone/clients/client-1/contact-1>
    >>> sampletype = api.create(bika_sampletypes, "SampleType", Prefix="H2O", MinimumVolume="100 ml")
    >>> sampletype
    <SampleType at /plone/bika_setup/bika_sampletypes/sampletype-1>

Create an `AnalysisCategory` (which categorizes different `AnalysisServices`), and add to it an `AnalysisService`.
This service matches the service specified in the file from which the import will be performed::

    >>> analysiscategory = api.create(bika_analysiscategories, "AnalysisCategory", title="Water")
    >>> analysiscategory
    <AnalysisCategory at /plone/bika_setup/bika_analysiscategories/analysiscategory-1>
    >>> analysisservice1 = api.create(bika_analysisservices,
    ...                              "AnalysisService",
    ...                              title="HIV06ml",
    ...                              ShortTitle="hiv06",
    ...                              Category=analysiscategory,
    ...                              Keyword="HIV06ml")
    >>> analysisservice1
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-1>

    >>> analysisservice2 = api.create(bika_analysisservices,
    ...                       'AnalysisService',
    ...                       title='Magnesium',
    ...                       ShortTitle='Mg',
    ...                       Category=analysiscategory,
    ...                       Keyword="Mg")
    >>> analysisservice2
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-2>
    >>> analysisservice3 = api.create(bika_analysisservices,
    ...                     'AnalysisService',
    ...                     title='Calcium',
    ...                     ShortTitle='Ca',
    ...                     Category=analysiscategory,
    ...                     Keyword="Ca")
    >>> analysisservice3
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-3>

    >>> total_calc = api.create(bika_calculations, 'Calculation', title='TotalMagCal')
    >>> total_calc.setFormula('[Mg] + [Ca]')

    >>> a_method = api.create(bika_methods, 'Method', title='A Method')
    >>> a_method.setCalculation(total_calc)

    >>> analysisservice4 = api.create(bika_analysisservices, 'AnalysisService', title='THCaCO3', Keyword="THCaCO3")
    >>> analysisservice4.setUseDefaultCalculation(False)
    >>> analysisservice4.setCalculation(total_calc)
    >>> analysisservice4.setMethod(a_method)
    >>> analysisservice4
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-4>

    >>> interim_calc = api.create(bika_calculations, 'Calculation', title='Test-Total-Pest')
    >>> pest1 = {'keyword': 'pest1', 'title': 'Pesticide 1', 'value': 0, 'type': 'int', 'hidden': False, 'unit': ''}
    >>> pest2 = {'keyword': 'pest2', 'title': 'Pesticide 2', 'value': 0, 'type': 'int', 'hidden': False, 'unit': ''}
    >>> pest3 = {'keyword': 'pest3', 'title': 'Pesticide 3', 'value': 0, 'type': 'int', 'hidden': False, 'unit': ''}
    >>> interims = [pest1, pest2, pest3]
    >>> interim_calc.setInterimFields(interims)
    >>> self.assertEqual(interim_calc.getInterimFields(), interims)
    >>> interim_calc.setFormula('((([pest1] > 0.0) or ([pest2] > .05) or ([pest3] > 10.0) ) and "PASS" or "FAIL" )')
    >>> analysisservice5 = api.create(bika_analysisservices, 'AnalysisService', title='Total Terpenes', Keyword="TotalTerpenes")
    >>> analysisservice5.setUseDefaultCalculation(False)
    >>> analysisservice5.setCalculation(interim_calc)
    >>> analysisservice5.setInterimFields(interims)
    >>> analysisservice5
    <AnalysisService at /plone/bika_setup/bika_analysisservices/analysisservice-5>

    >>> service_uids = [
    ...     analysisservice1.UID(),
    ...     analysisservice2.UID(),
    ...     analysisservice3.UID(),
    ...     analysisservice4.UID(),
    ...     analysisservice5.UID()
    ... ]

Create an `AnalysisRequest` with this `AnalysisService` and receive it::

    >>> values = {
    ...           'Client': client.UID(),
    ...           'Contact': contact.UID(),
    ...           'SamplingDate': date_now,
    ...           'DateSampled': date_now,
    ...           'SampleType': sampletype.UID()
    ...          }
    >>> ar = create_analysisrequest(client, request, values, service_uids)
    >>> ar
    <AnalysisRequest at /plone/clients/client-1/H2O-0001>
    >>> ar.getReceivedBy()
    ''
    >>> wf = api.get_tool('portal_workflow')
    >>> wf.doActionFor(ar, 'receive')
    >>> ar.getReceivedBy()
    'test_user_1_'
