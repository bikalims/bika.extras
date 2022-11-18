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


from pkg_resources import resource_filename

from Products.Archetypes.event import ObjectInitializedEvent
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFPlone.utils import safe_unicode
from zope.event import notify

from bika.lims import logger
from bika.lims.utils import tmpID
from bika.lims.idserver import renameAfterCreation
from senaite.core.exportimport.setupdata import addDocument
from senaite.core.exportimport.setupdata import read_file
from senaite.core.exportimport.setupdata import Float
from senaite.core.exportimport.setupdata import WorksheetImporter


class Analysis_Specifications(WorksheetImporter):

    def resolve_service(self, row):
        bsc = getToolByName(self.context, "senaite_catalog_setup")
        service = bsc(
            portal_type="AnalysisService",
            title=safe_unicode(row["service"])
        )
        if not service:
            service = bsc(
                portal_type="AnalysisService",
                getKeyword=safe_unicode(row["service"])
            )
        service = service[0].getObject()
        return service

    def Import(self):
        bucket = {}
        pc = getToolByName(self.context, "portal_catalog")
        bsc = getToolByName(self.context, "senaite_catalog_setup")
        # collect up all values into the bucket
        for row in self.get_rows(3):
            title = row.get("Title", False)
            if not title:
                title = row.get("title", False)
                if not title:
                    continue
            parent = row["Client_title"] if row["Client_title"] else "lab"
            st = row["SampleType_title"] if row["SampleType_title"] else ""
            description = row.get("Description", "")
            service = self.resolve_service(row)

            if parent not in bucket:
                bucket[parent] = {}
            if title not in bucket[parent]:
                bucket[parent][title] = {"sampletype": st, "resultsrange": []}
                bucket[parent][title]["description"] = description
            bucket[parent][title]["resultsrange"].append({
                "keyword": service.getKeyword(),
                "min": row["min"] if row["min"] else "0",
                "max": row["max"] if row["max"] else "0",
            })
        # write objects.
        for parent in bucket.keys():
            for title in bucket[parent]:
                if parent == "lab":
                    folder = self.context.bika_setup.bika_analysisspecs
                else:
                    proxy = pc(portal_type="Client", getName=safe_unicode(parent))[0]
                    folder = proxy.getObject()
                st = bucket[parent][title]["sampletype"]
                resultsrange = bucket[parent][title]["resultsrange"]
                description = bucket[parent][title]["description"]
                if st:
                    st_uid = bsc(portal_type="SampleType", title=safe_unicode(st))[0].UID
                obj = _createObjectByType("AnalysisSpec", folder, tmpID())
                obj.edit(title=title)
                obj.edit(description=description)
                obj.setResultsRange(resultsrange)
                if st:
                    obj.setSampleType(st_uid)
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Instruments(WorksheetImporter):

    def Import(self):
        folder = self.context.bika_setup.bika_instruments
        bsc = getToolByName(self.context, 'senaite_catalog_setup')
        pc = getToolByName(self.context, 'portal_catalog')
        for row in self.get_rows(3):
            if ('Type' not in row
                or 'Supplier' not in row
                or 'Brand' not in row):
                logger.info("Unable to import '%s'. Missing supplier, manufacturer or type" % row.get('title',''))
                continue

            obj = _createObjectByType("Instrument", folder, tmpID())

            obj.edit(
                title=row.get('title', ''),
                AssetNumber=row.get('assetnumber', ''),
                description=row.get('description', ''),
                Type=row.get('Type', ''),
                Brand=row.get('Brand', ''),
                Model=row.get('Model', ''),
                SerialNo=row.get('SerialNo', ''),
                DataInterface=row.get('DataInterface', ''),
                Location=row.get('Location', ''),
                InstallationDate=row.get('Instalationdate', ''),
                UserManualID=row.get('UserManualID', ''),
            )
            instrumenttype = self.get_object(bsc, 'InstrumentType', title=row.get('Type'))
            manufacturer = self.get_object(bsc, 'Manufacturer', title=row.get('Brand'))
            supplier = self.get_object(pc, 'Supplier', getName=row.get('Supplier', ''))
            method = self.get_object(pc, 'Method', title=row.get('Method'))
            obj.setInstrumentType(instrumenttype)
            obj.setManufacturer(manufacturer)
            obj.setSupplier(supplier)
            if method:
                obj.setMethods([method])
                obj.setMethod(method)

            # Attaching the instrument's photo
            if row.get('Photo', None):
                path = resource_filename(
                    self.dataset_project,
                    "setupdata/%s/%s" % (self.dataset_name,
                                         row['Photo'])
                )
                try:
                    file_data = read_file(path)
                    obj.setPhoto(file_data)
                except Exception as msg:
                    file_data = None
                    logger.warning(msg[0] + " Error on sheet: " + self.sheetname)

            # Attaching the Installation Certificate if exists
            if row.get('InstalationCertificate', None):
                path = resource_filename(
                    self.dataset_project,
                    "setupdata/%s/%s" % (self.dataset_name,
                                         row['InstalationCertificate'])
                )
                try:
                    file_data = read_file(path)
                    obj.setInstallationCertificate(file_data)
                except Exception as msg:
                    logger.warning(msg[0] + " Error on sheet: " + self.sheetname)

            # Attaching the Instrument's manual if exists
            if row.get('UserManualFile', None):
                row_dict = {'DocumentID': row.get('UserManualID', 'manual'),
                            'DocumentVersion': '',
                            'DocumentLocation': '',
                            'DocumentType': 'Manual',
                            'File': row.get('UserManualFile', None)
                            }
                addDocument(self, row_dict, obj)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Methods(WorksheetImporter):

    def load_instrument_methods(self):
        sheetname = 'Instrument Methods'
        worksheet = self.workbook[sheetname]
        self.instrument_methods = {}
        bsc = getToolByName(self.context, 'senaite_catalog_setup')
        if not worksheet:
            return
        for i, row in enumerate(self.get_rows(3, worksheet=worksheet)):
            if not row.get('Instrument_title', '') or not row.get('Method_title', ''):
                continue
            if row['Method_title'] not in self.instrument_methods.keys():
                self.instrument_methods[row['Method_title']] = []
            instrument = self.get_object(bsc,
                             'Instrument', title=row['Instrument_title'])
            if instrument:
                self.instrument_methods[row['Method_title']].append(instrument)

    def Import(self):
        self.load_instrument_methods()
        folder = self.context.methods
        bsc = getToolByName(self.context, 'senaite_catalog_setup')
        for row in self.get_rows(3):
            if row['title']:
                calculation = self.get_object(bsc, 'Calculation', row.get('Calculation_title'))
                instrument = self.get_object(bsc, 'Instrument', Title=row.get('Instrument_title'))
                instruments = self.instrument_methods.get(row['title'], [])
                if instrument:
                    instruments.append(instrument)
                supplier = self.get_object(bsc, 'Supplier',Title=row.get('Subcontractor_title'))

                if calculation:
                    calculation = calculation.UID()
                obj = _createObjectByType("Method", folder, tmpID())
                obj.edit(
                    title=row['title'],
                    description=row.get('description', ''),
                    Instructions=row.get('Instructions', ''),
                    ManualEntryOfResults=row.get('ManualEntryOfResults', True),
                    Calculations=[calculation],
                    Calculation=calculation,
                    MethodID=row.get('MethodID', ''),
                    Accredited=row.get('Accredited', True),
                    Supplier=supplier,
                    Instruments=[inst.UID() for inst in instruments],

                )
                # Obtain all created methods
                catalog = getToolByName(self.context, 'portal_catalog')
                methods_brains = catalog.searchResults({'portal_type': 'Method'})
                # If a the new method has the same MethodID as a created method, remove MethodID value.
                for methods in methods_brains:
                    if methods.getObject().get('MethodID', '') != '' and methods.getObject.get('MethodID', '') == obj['MethodID']:
                        obj.edit(MethodID='')

                if row['MethodDocument']:
                    path = resource_filename(
                        self.dataset_project,
                        "setupdata/%s/%s" % (self.dataset_name,
                                             row['MethodDocument'])
                    )
                    try:
                        file_data = read_file(path)
                        obj.setMethodDocument(file_data)
                    except Exception as msg:
                        logger.warning(msg[0] + " Error on sheet: " + self.sheetname)

                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))


class Analysis_Services(WorksheetImporter):

    def load_interim_fields(self):
        # preload AnalysisService InterimFields sheet
        sheetname = 'AnalysisService InterimFields'
        worksheet = self.workbook[sheetname]
        if not worksheet:
            return
        self.service_interims = {}
        rows = self.get_rows(3, worksheet=worksheet)
        for row in rows:
            service_title = row['Service_title']
            if service_title not in self.service_interims.keys():
                self.service_interims[service_title] = []
            self.service_interims[service_title].append({
                'keyword': row['keyword'],
                'title': row.get('title', ''),
                'type': 'int',
                'value': row['value'],
                'unit': row['unit'] and row['unit'] or ''})

    def load_result_options(self):
        bsc = getToolByName(self.context, 'senaite_catalog_setup')
        sheetname = 'AnalysisService ResultOptions'
        worksheet = self.workbook[sheetname]
        if not worksheet:
            return
        for row in self.get_rows(3, worksheet=worksheet):
            service = self.get_object(bsc, 'AnalysisService',
                                      row.get('Service_title'))
            if not service:
                return
            sro = service.getResultOptions()
            sro.append({'ResultValue': row['ResultValue'],
                        'ResultText': row['ResultText']})
            service.setResultOptions(sro)

    def load_service_uncertainties(self):
        bsc = getToolByName(self.context, 'senaite_catalog_setup')
        sheetname = 'Analysis Service Uncertainties'
        worksheet = self.workbook[sheetname]
        if not worksheet:
            return

        bucket = {}
        count = 0
        for row in self.get_rows(3, worksheet=worksheet):
            count += 1
            service = self.get_object(bsc, 'AnalysisService',
                                      row.get('Service_title'))
            if not service:
                warning = "Unable to load an Analysis Service uncertainty. Service '%s' not found." % row.get('Service_title')
                logger.warning(warning)
                continue
            service_uid = service.UID()
            if service_uid not in bucket:
                bucket[service_uid] = []
            bucket[service_uid].append(
                {'intercept_min': row['Range Min'],
                 'intercept_max': row['Range Max'],
                 'errorvalue': row['Uncertainty Value']}
            )
            if count > 500:
                self.write_bucket(bucket)
                bucket = {}
        if bucket:
            self.write_bucket(bucket)

    def get_methods(self, service_title, default_method):
        """ Return an array of objects of the type Method in accordance to the
            methods listed in the 'AnalysisService Methods' sheet and service
            set in the parameter service_title.
            If default_method is set, it will be included in the returned
            array.
        """
        return self.get_relations(service_title,
                                default_method,
                                'Method',
                                'portal_catalog',
                                'AnalysisService Methods',
                                'Method_title')

    def get_instruments(self, service_title, default_instrument):
        """ Return an array of objects of the type Instrument in accordance to
            the instruments listed in the 'AnalysisService Instruments' sheet
            and service set in the parameter 'service_title'.
            If default_instrument is set, it will be included in the returned
            array.
        """
        return self.get_relations(service_title,
                                default_instrument,
                                'Instrument',
                                'senaite_catalog_setup',
                                'AnalysisService Instruments',
                                'Instrument_title')

    def get_relations(self, service_title, default_obj, obj_type, catalog_name, sheet_name, column):
        """ Return an array of objects of the specified type in accordance to
            the object titles defined in the sheet specified in 'sheet_name' and
            service set in the paramenter 'service_title'.
            If a default_obj is set, it will be included in the returned array.
        """
        out_objects = [default_obj] if default_obj else []
        cat = getToolByName(self.context, catalog_name)
        worksheet = self.workbook[sheet_name]
        if not worksheet:
            return out_objects
        for row in self.get_rows(3, worksheet=worksheet):
            row_as_title = row.get('Service_title')
            if not row_as_title:
                return out_objects
            elif row_as_title != service_title:
                continue
            obj = self.get_object(cat, obj_type, row.get(column))
            if obj:
                if default_obj and default_obj.UID() == obj.UID():
                    continue
                out_objects.append(obj)
        return out_objects

    def write_bucket(self, bucket):
        bsc = getToolByName(self.context, 'senaite_catalog_setup')
        for service_uid, uncertainties in bucket.items():
            obj = bsc(UID=service_uid)[0].getObject()
            _uncert = list(obj.getUncertainties())
            _uncert.extend(uncertainties)
            obj.setUncertainties(_uncert)

    def Import(self):
        self.load_interim_fields()
        folder = self.context.bika_setup.bika_analysisservices
        bsc = getToolByName(self.context, 'senaite_catalog_setup')
        pc = getToolByName(self.context, 'portal_catalog')
        for row in self.get_rows(3):
            if not row['title']:
                continue

            obj = _createObjectByType("AnalysisService", folder, tmpID())
            MTA = {
                'days': self.to_int(row.get('MaxTimeAllowed_days',0),0),
                'hours': self.to_int(row.get('MaxTimeAllowed_hours',0),0),
                'minutes': self.to_int(row.get('MaxTimeAllowed_minutes',0),0),
            }
            category = self.get_object(bsc, 'AnalysisCategory', row.get('AnalysisCategory_title'))
            department = self.get_object(bsc, 'Department', row.get('Department_title'))
            container = self.get_object(bsc, 'Container', row.get('Container_title'))
            preservation = self.get_object(bsc, 'Preservation', row.get('Preservation_title'))

            # Analysis Service - Method considerations:
            # One Analysis Service can have 0 or n Methods associated (field
            # 'Methods' from the Schema).
            # If the Analysis Service has at least one method associated, then
            # one of those methods can be set as the defualt method (field
            # '_Method' from the Schema).
            #
            # To make it easier, if a DefaultMethod is declared in the
            # Analysis_Services spreadsheet, but the same AS has no method
            # associated in the Analysis_Service_Methods spreadsheet, then make
            # the assumption that the DefaultMethod set in the former has to be
            # associated to the AS although the relation is missing.
            defaultmethod = self.get_object(pc, 'Method', row.get('DefaultMethod_title'))
            methods = self.get_methods(row['title'], defaultmethod)
            if not defaultmethod and methods:
                defaultmethod = methods[0]

            # Analysis Service - Instrument considerations:
            # By default, an Analysis Services will be associated automatically
            # with several Instruments due to the Analysis Service - Methods
            # relation (an Instrument can be assigned to a Method and one Method
            # can have zero or n Instruments associated). There is no need to
            # set this assignment directly, the AnalysisService object will
            # find those instruments.
            # Besides this 'automatic' behavior, an Analysis Service can also
            # have 0 or n Instruments manually associated ('Instruments' field).
            # In this case, the attribute 'AllowInstrumentEntryOfResults' should
            # be set to True.
            #
            # To make it easier, if a DefaultInstrument is declared in the
            # Analysis_Services spreadsheet, but the same AS has no instrument
            # associated in the AnalysisService_Instruments spreadsheet, then
            # make the assumption the DefaultInstrument set in the former has
            # to be associated to the AS although the relation is missing and
            # the option AllowInstrumentEntryOfResults will be set to True.
            defaultinstrument = self.get_object(bsc, 'Instrument', row.get('DefaultInstrument_title'))
            instruments = self.get_instruments(row['title'], defaultinstrument)
            allowinstrentry = True if instruments else False
            if not defaultinstrument and instruments:
                defaultinstrument = instruments[0]

            # The manual entry of results can only be set to false if the value
            # for the attribute "InstrumentEntryOfResults" is False.
            allowmanualentry = True if not allowinstrentry else row.get('ManualEntryOfResults', True)

            # Analysis Service - Calculation considerations:
            # By default, the AnalysisService will use the Calculation associated
            # to the Default Method (the field "UseDefaultCalculation"==True).
            # If the Default Method for this AS doesn't have any Calculation
            # associated and the field "UseDefaultCalculation" is True, no
            # Calculation will be used for this AS ("_Calculation" field is
            # reserved and should not be set directly).
            #
            # To make it easier, if a Calculation is set by default in the
            # spreadsheet, then assume the UseDefaultCalculation has to be set
            # to False.
            deferredcalculation = self.get_object(bsc, 'Calculation', row.get('Calculation_title'))
            usedefaultcalculation = False if deferredcalculation else True
            _calculation = deferredcalculation if deferredcalculation else \
                            (defaultmethod.getCalculation() if defaultmethod else None)

            if _calculation:
                _calculation = _calculation.UID()
            obj.edit(
                title=row['title'],
                ShortTitle=row.get('ShortTitle', row['title']),
                description=row.get('description', ''),
                Keyword=row['Keyword'],
                PointOfCapture=row['PointOfCapture'].lower(),
                Category=category,
                Department=department,
                Unit=row['Unit'] and row['Unit'] or None,
                Precision=row['Precision'] and str(row['Precision']) or '0',
                ExponentialFormatPrecision=str(self.to_int(row.get('ExponentialFormatPrecision',7),7)),
                LowerDetectionLimit='%06f' % self.to_float(row.get('LowerDetectionLimit', '0.0'), 0),
                UpperDetectionLimit='%06f' % self.to_float(row.get('UpperDetectionLimit', '1000000000.0'), 1000000000.0),
                DetectionLimitSelector=self.to_bool(row.get('DetectionLimitSelector',0)),
                MaxTimeAllowed=MTA,
                Price="%02f" % Float(row['Price']),
                BulkPrice="%02f" % Float(row['BulkPrice']),
                VAT="%02f" % Float(row['VAT']),
                Method=defaultmethod,
                Methods=methods,
                ManualEntryOfResults=allowmanualentry,
                InstrumentEntryOfResults=allowinstrentry,
                Instrument=defaultinstrument,
                Instruments=instruments,
                Calculation=_calculation,
                UseDefaultCalculation=usedefaultcalculation,
                DuplicateVariation="%02f" % Float(row['DuplicateVariation']),
                Accredited=self.to_bool(row['Accredited']),
                InterimFields=hasattr(self, 'service_interims') and self.service_interims.get(
                    row['title'], []) or [],
                Separate=self.to_bool(row.get('Separate', False)),
                Container=container,
                Preservation=preservation,
                CommercialID=row.get('CommercialID', ''),
                ProtocolID=row.get('ProtocolID', '')
            )
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))
        self.load_result_options()
        self.load_service_uncertainties()


class AR_Templates(WorksheetImporter):

    def load_artemplate_analyses(self):
        sheetname = 'AR Template Analyses'
        worksheet = self.workbook[sheetname]
        self.artemplate_analyses = {}
        if not worksheet:
            return
        bsc = getToolByName(self.context, 'senaite_catalog_setup')
        for row in self.get_rows(3, worksheet=worksheet):
            # XXX service_uid is not a uid
            service = self.get_object(bsc, 'AnalysisService',
                                      row.get('service_uid'))
            if not service:
                continue

            if row['ARTemplate'] not in self.artemplate_analyses.keys():
                self.artemplate_analyses[row['ARTemplate']] = []
            self.artemplate_analyses[row['ARTemplate']].append(
                {'service_uid': service.UID(),
                 'partition': row['partition']
                 }
            )

    def load_artemplate_partitions(self):
        sheetname = 'AR Template Partitions'
        worksheet = self.workbook[sheetname]
        self.artemplate_partitions = {}
        bsc = getToolByName(self.context, 'senaite_catalog_setup')
        if not worksheet:
            return
        for row in self.get_rows(3, worksheet=worksheet):
            if row['ARTemplate'] not in self.artemplate_partitions.keys():
                self.artemplate_partitions[row['ARTemplate']] = []
            container = self.get_object(bsc, 'Container',
                                        row.get('container'))
            preservation = self.get_object(bsc, 'Preservation',
                                           row.get('preservation'))
            self.artemplate_partitions[row['ARTemplate']].append({
                'part_id': row['part_id'],
                'Container': container.Title() if container else None,
                'container_uid': container.UID() if container else None,
                'Preservation': preservation.Title() if preservation else None,
                'preservation_uid': preservation.UID()} if preservation else None)

    def Import(self):
        self.load_artemplate_analyses()
        self.load_artemplate_partitions()
        folder = self.context.bika_setup.bika_artemplates
        bsc = getToolByName(self.context, 'senaite_catalog_setup')
        pc = getToolByName(self.context, 'portal_catalog')
        for row in self.get_rows(3):
            if not row['title']:
                continue
            analyses = self.artemplate_analyses[row['title']]
            client_title = row['Client_title'] or 'lab'
            if row['title'] in self.artemplate_partitions:
                partitions = self.artemplate_partitions[row['title']]
            else:
                partitions = [{'part_id': 'part-1',
                               'container': '',
                               'preservation': ''}]

            if client_title == 'lab':
                folder = self.context.bika_setup.bika_artemplates
            else:
                folder = pc(portal_type='Client',
                            getName=client_title)[0].getObject()

            sampletype = self.get_object(bsc, 'SampleType',
                                         row.get('SampleType_title'))
            samplepoint = self.get_object(bsc, 'SamplePoint',
                                         row.get('SamplePoint_title'))

            obj = _createObjectByType("ARTemplate", folder, tmpID())
            obj.edit(
                title=str(row['title']),
                description=row.get('description', ''),
                Remarks=row.get('Remarks', ''),)
            obj.setSampleType(sampletype)
            obj.setSamplePoint(samplepoint)
            obj.setPartitions(partitions)
            obj.setAnalyses(analyses)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Reference_Definitions(WorksheetImporter):

    def load_reference_definition_results(self):
        sheetname = 'Reference Definition Results'
        worksheet = self.workbook[sheetname]
        if not worksheet:
            sheetname = 'Reference Definition Values'
            worksheet = self.workbook[sheetname]
            if not worksheet:
                return
        self.results = {}
        if not worksheet:
            return
        bsc = getToolByName(self.context, 'senaite_catalog_setup')
        for row in self.get_rows(3, worksheet=worksheet):
            if row['ReferenceDefinition_title'] not in self.results.keys():
                self.results[row['ReferenceDefinition_title']] = []
            service = self.get_object(bsc, 'AnalysisService',
                    row.get('service'), **{"getKeyword": row.get("Keyword")})
            if not service:
                continue
            self.results[
                row['ReferenceDefinition_title']].append({
                    'uid': service.UID(),
                    'result': row['result'] if row['result'] else '0',
                    'min': row['min'] if row['min'] else '0',
                    'max': row['max'] if row['max'] else '0'})

    def Import(self):
        self.load_reference_definition_results()
        folder = self.context.bika_setup.bika_referencedefinitions
        for row in self.get_rows(3):
            if not row['title']:
                continue
            obj = _createObjectByType("ReferenceDefinition", folder, tmpID())
            obj.edit(
                title=row['title'],
                description=row.get('description', ''),
                Blank=self.to_bool(row['Blank']),
                ReferenceResults=self.results.get(row['title'], []),
                Hazardous=self.to_bool(row['Hazardous']))
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


class Worksheet_Templates(WorksheetImporter):

    def load_wst_layouts(self):
        sheetname = 'Worksheet Template Layouts'
        worksheet = self.workbook[sheetname]
        self.wst_layouts = {}
        if not worksheet:
            return
        for row in self.get_rows(3, worksheet=worksheet):
            if row['WorksheetTemplate_title'] \
               not in self.wst_layouts.keys():
                self.wst_layouts[
                    row['WorksheetTemplate_title']] = []
            self.wst_layouts[
                row['WorksheetTemplate_title']].append({
                    'pos': row['pos'],
                    'type': row['type'],
                    'blank_ref': row['blank_ref'],
                    'control_ref': row['control_ref'],
                    'dup': row['dup']})

    def load_wst_services(self):
        sheetname = 'Worksheet Template Services'
        worksheet = self.workbook[sheetname]
        self.wst_services = {}
        if not worksheet:
            return
        bsc = getToolByName(self.context, 'senaite_catalog_setup')
        for row in self.get_rows(3, worksheet=worksheet):
            service = self.get_object(bsc, 'AnalysisService',
                                      row.get('service'))
            if row['WorksheetTemplate_title'] not in self.wst_services.keys():
                self.wst_services[row['WorksheetTemplate_title']] = []
            if not service:
                continue
            self.wst_services[
                row['WorksheetTemplate_title']].append(service.UID())

    def Import(self):
        self.load_wst_services()
        self.load_wst_layouts()
        folder = self.context.bika_setup.bika_worksheettemplates
        for row in self.get_rows(3):
            if row['title']:
                obj = _createObjectByType("WorksheetTemplate", folder, tmpID())
                obj.edit(
                    title=row['title'],
                    description=row.get('description', ''),
                    Layout=self.wst_layouts[row['title']])
                obj.setService(self.wst_services[row['title']])
                obj.unmarkCreationFlag()
                renameAfterCreation(obj)
                notify(ObjectInitializedEvent(obj))

class Supplier_Contacts(WorksheetImporter):

    def Import(self):

        bsc = getToolByName(self.context, 'senaite_catalog_setup')
        for row in self.get_rows(3):
            if not row['Supplier_Name']:
                continue
            if not row['Firstname']:
                continue
            folder = bsc(portal_type="Supplier",
                         Title=row['Supplier_Name'])
            if not folder:
                continue
            folder = folder[0].getObject()
            obj = _createObjectByType("SupplierContact", folder, tmpID())
            obj.edit(
                Firstname=row['Firstname'],
                Surname=row.get('Surname', ''),
                Username=row.get('Username'),
                Department=row.get('Department'),
                JobTitle=row.get('JobTitle')
            )
            self.fill_contactfields(row, obj)
            self.fill_addressfields(row, obj)
            obj.unmarkCreationFlag()
            renameAfterCreation(obj)
            notify(ObjectInitializedEvent(obj))


