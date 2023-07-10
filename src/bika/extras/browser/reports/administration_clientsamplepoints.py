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
from senaite.core.catalog import SETUP_CATALOG


class Report(RA):

    def __call__(self):
        setup_catalog = api.get_tool(SETUP_CATALOG)
        client_catalog = api.get_tool(CLIENT_CATALOG)
        rc = api.get_tool('reference_catalog')
        self.report_content = {}
        parms = []
        headings = {}
        headings['header'] = _("Client Sample Points")
        headings['subheader'] = _("Client Sample Points")

        count_all = 0
        query = {'portal_type': 'SamplePoint',
                 'is_active': True,
                 'sort_order': 'reverse'}

        client_query = {'portal_type': 'Client',
                        'is_active': True,
                        'sort_order': 'reverse'}
        if 'ClientUID' in self.request.form:
            client_uid = self.request.form['ClientUID']
            client_query['UID'] = client_uid
            client = rc.lookupObject(client_uid)
            client_title = client.Title()
        else:
            client_title = 'All'
        parms.append(
            {'title': _('Client'),
             'value': client_title,
             'type': 'text'})

        # and now lets do the actual report lines
        formats = {'columns': 5,
                   'col_heads': [_('Client'),
                                 _('Client ID'),
                                 _('Sample Point Name'),
                                 _('Sample Point Description'),
                                 _('Sample Types'),
                                 ],
                   'class': '',
                   }

        datalines = []

        if client_title != "All":
            for brain in client_catalog(client_query):
                client = brain.getObject()
                path = {"query": api.get_path(client), "depth": 1}
                query["path"] = path
                for brain in setup_catalog(query):
                    dataline = []
                    sample_point = brain.getObject()
                    dataitem = {'value': client.getName() if client else ""}
                    dataline.append(dataitem)
                    dataitem = {'value': client.getClientID() if client else ""}
                    dataline.append(dataitem)
                    dataitem = {'value': sample_point.Title()}
                    dataline.append(dataitem)
                    dataitem = {'value': sample_point.Description()}
                    dataline.append(dataitem)
                    sample_types = sample_point.getSampleTypes()
                    dataitem = {'value': ','.join([i.Title() for i in sample_types])}
                    dataline.append(dataitem)

                    datalines.append(dataline)
                    count_all += 1
                query.pop("path")

        if client_title == "All":
            for brain in setup_catalog(query):
                obj = brain.getObject()
                dataline = []
                client = obj.getClient()
                dataitem = {'value': client.getName() if client else ""}
                dataline.append(dataitem)
                dataitem = {'value': client.getClientID() if client else ""}
                dataline.append(dataitem)
                dataitem = {'value': obj.Title()}
                dataline.append(dataitem)
                dataitem = {'value': obj.Description()}
                dataline.append(dataitem)
                sample_types = obj.getSampleTypes()
                dataitem = {'value': ','.join([i.Title() for i in sample_types])}
                dataline.append(dataitem)

                datalines.append(dataline)
                count_all += 1

        if self.request.get('output_format', '') == 'CSV':
            return self.generate_csv(formats["col_heads"], datalines)

        # table footer data
        footlines = []
        footline = []
        footitem = {'value': _('Client Sample Points'),
                    'colspan': 4,
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
                'Client ID': safe_unicode(row[1]['value']).encode(t),
                'Sample Point Name': safe_unicode(row[2]['value']).encode(t),
                'Sample Point Description': safe_unicode(row[3]['value']).encode(t),
                'Sample Types': safe_unicode(row[4]['value']).encode(t),
            })
        report_data = output.getvalue()
        output.close()

        date = datetime.datetime.now().strftime("%Y%m%d%H%M")
        setheader = self.request.RESPONSE.setHeader
        setheader('Content-Type', 'text/csv')
        setheader("Content-Disposition",
                  "attachment;filename=\"client_sample_points_%s.csv\"" % date)
        self.request.RESPONSE.write(report_data)
