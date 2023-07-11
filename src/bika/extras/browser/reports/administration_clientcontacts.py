# -*- coding: utf-8 -*-

import csv
import datetime
from Products.CMFPlone.utils import safe_unicode
from six import StringIO

from bika.extras import _
from bika.lims import api
from bika.lims.browser.reports.administration_arsnotinvoiced import Report as RA
from bika.lims.utils import t
from senaite.core.catalog import CLIENT_CATALOG


class Report(RA):

    def __call__(self):
        client_catalog = api.get_tool(CLIENT_CATALOG)
        rc = api.get_tool('reference_catalog')
        self.report_content = {}
        parms = []
        headings = {}
        headings['header'] = _("Client Contacts")
        headings['subheader'] = _("Client Contacts")

        count_all = 0

        query = {'portal_type': 'Client',
                 'is_active': True,
                 "sort_on": "sortable_title",
                 "sort_order": "ascending"}

        if 'ClientUID' in self.request.form:
            client_uid = self.request.form['ClientUID']
            query['UID'] = client_uid
            client = rc.lookupObject(client_uid)
            client_title = client.Title()
        else:
            client_title = 'All'
        parms.append(
            {'title': _('Client: '),
             'value': client_title,
             'type': 'text'})

        # and now lets do the actual report lines
        formats = {'columns': 9,
                   'col_heads': [_('Client'),
                                 _('Salutation'),
                                 _('First Name'),
                                 _('Middle Name'),
                                 _('Surname'),
                                 _('Job Title'),
                                 _('Email Address'),
                                 _('Business Phone'),
                                 _('Mobile Phone'),
                                 ],
                   'class': '',
                   }

        datalines = []

        for brain in client_catalog(query):
            obj = brain.getObject()
            contacts = obj.objectValues('Contact')
            for contact in contacts:
                dataline = []
                dataitem = {'value': obj.getName()}
                dataline.append(dataitem)
                dataitem = {'value': contact.getSalutation()}
                dataline.append(dataitem)
                dataitem = {'value': contact.getFirstname()}
                dataline.append(dataitem)
                dataitem = {'value': contact.getMiddlename()}
                dataline.append(dataitem)
                dataitem = {'value': contact.getSurname()}
                dataline.append(dataitem)
                dataitem = {'value': contact.getJobTitle()}
                dataline.append(dataitem)
                dataitem = {'value': contact.getEmailAddress()}
                dataline.append(dataitem)
                dataitem = {'value': contact.getBusinessPhone()}
                dataline.append(dataitem)
                dataitem = {'value': contact.getMobilePhone()}
                dataline.append(dataitem)

                datalines.append(dataline)
                count_all += 1

        # Blank line for PDF
        if self.request.get('output_format', '') == 'PDF':
            blank = [{"value": "."}] * formats.get("columns", 9)
            datalines.append(blank)

        if self.request.get('output_format', '') == 'CSV':
            return self.generate_csv(formats["col_heads"], datalines)

        # table footer data
        footlines = []
        footline = []
        footitem = {'value': _('Total Client Contacts'),
                    'colspan': 8,
                    'class': 'total_label'}
        footline.append(footitem)
        footitem = {'value': count_all}
        footline.append(footitem)
        footlines.append(footline)

        self.report_content = {
            'headings': headings,
            'parms': parms,
            'formats': formats,
            'datalines': datalines,
            'footings': footlines}

        return {'report_title': t(headings['header']),
                'report_data': self.template()}

    def generate_csv(self, headers, data_lines):
        """Generates and writes a CSV to request's reposonse
        """
        fieldnames = headers
        output = StringIO()
        dw = csv.DictWriter(output, extrasaction='ignore',
                            fieldnames=fieldnames)
        dw.writerow(dict((fn, fn) for fn in fieldnames))
        t = 'utf-8'
        for row in data_lines:
            dw.writerow({
                'Client': safe_unicode(row[0]['value']).encode(t),
                'Salutation': safe_unicode(row[1]['value']).encode(t),
                'First Name': safe_unicode(row[2]['value']).encode(t),
                'Middle Name': safe_unicode(row[3]['value']).encode(t),
                'Surname': safe_unicode(row[4]['value']).encode(t),
                'Job Title': safe_unicode(row[5]['value']).encode(t),
                'Email Address': safe_unicode(row[6]['value']).encode(t),
                'Business Phone': safe_unicode(row[7]['value']).encode(t),
                'Mobile Phone': safe_unicode(row[8]['value']).encode(t),
            })

        report_data = output.getvalue()
        output.close()

        date = datetime.datetime.now().strftime("%Y-%m-%d %H%M")
        setheader = self.request.RESPONSE.setHeader
        setheader('Content-Type', 'text/csv')
        setheader("Content-Disposition",
                  "attachment;filename=\"Client Contacts %s.csv\"" % date)
        self.request.RESPONSE.write(report_data)
