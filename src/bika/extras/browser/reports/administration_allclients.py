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
        self.report_content = {}
        parms = []
        headings = {}
        headings['header'] = _("All Clients")
        headings['subheader'] = _("All Clients")

        count_all = 0

        query = {'portal_type': 'Client',
                 'is_active': True,
                 "sort_on": "sortable_title",
                 "sort_order": "ascending"}

        # and now lets do the actual report lines
        formats = {'columns': 7,
                   'col_heads': [_('Client'),
                                 _('Client ID'),
                                 _('Email Address'),
                                 _('CC Emails'),
                                 _('Phone Number'),
                                 _('Bulk Discount'),
                                 _('Member Discount'),
                                 ],
                   'class': '',
                   }

        datalines = []

        for brain in client_catalog(query):
            obj = brain.getObject()

            dataline = []
            dataitem = {'value': obj.getName()}
            dataline.append(dataitem)
            dataitem = {'value': obj.ClientID}
            dataline.append(dataitem)
            dataitem = {'value': obj.EmailAddress}
            dataline.append(dataitem)
            dataitem = {'value': obj.CCEmails}
            dataline.append(dataitem)
            dataitem = {'value': obj.Phone}
            dataline.append(dataitem)
            dataitem = {'value': "Y" if obj.BulkDiscount else ""}
            dataline.append(dataitem)
            dataitem = {'value': "Y" if obj.MemberDiscountApplies else ""}
            dataline.append(dataitem)
            if self.request.get('output_format', '') == 'CSV':
                dataitem = {'value': obj.PhysicalAddress.get("address")}
                dataline.append(dataitem)
                dataitem = {'value': _(obj.PhysicalAddress.get("district"))}
                dataline.append(dataitem)
                dataitem = {'value': _(obj.PhysicalAddress.get("state"))}
                dataline.append(dataitem)
                dataitem = {'value': _(obj.PhysicalAddress.get("city"))}
                dataline.append(dataitem)
                dataitem = {'value': _(obj.PhysicalAddress.get("zip"))}
                dataline.append(dataitem)
                dataitem = {'value': _(obj.PhysicalAddress.get("country"))}
                dataline.append(dataitem)
                dataitem = {'value': _(obj.PostalAddress.get("address"))}
                dataline.append(dataitem)
                dataitem = {'value': _(obj.PostalAddress.get("district"))}
                dataline.append(dataitem)
                dataitem = {'value': _(obj.PostalAddress.get("state"))}
                dataline.append(dataitem)
                dataitem = {'value': _(obj.PostalAddress.get("city"))}
                dataline.append(dataitem)
                dataitem = {'value': _(obj.PostalAddress.get("zip"))}
                dataline.append(dataitem)
                dataitem = {'value': _(obj.PostalAddress.get("country"))}
                dataline.append(dataitem)

            datalines.append(dataline)

            count_all += 1

        if self.request.get('output_format', '') == 'CSV':
            return self.generate_csv(formats["col_heads"], datalines)

        # table footer data
        footlines = []
        footline = []
        footitem = {'value': _('Total Clients'),
                    'colspan': 6,
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
        fieldnames.extend([_('Physical Address'),
                           _('District'),
                           _('State'),
                           _('City'),
                           _('Postal Code'),
                           _('Country'),
                           _('Postal Address'),
                           _('District.'),
                           _('State.'),
                           _('City.'),
                           _('Postal Code.'),
                           _('Country.'),
                           ])
        output = StringIO()
        dw = csv.DictWriter(output, extrasaction='ignore',
                            fieldnames=fieldnames)
        dw.writerow(dict((fn, fn) for fn in fieldnames))
        t = 'utf-8'
        for row in data_lines:
            dw.writerow({
                'Client': safe_unicode(row[0]['value']).encode(t),
                'Client ID': safe_unicode(row[1]['value']).encode(t),
                'Email Address': safe_unicode(row[2]['value']).encode(t),
                'CC Emails': safe_unicode(row[3]['value']).encode(t),
                'Phone Number': safe_unicode(row[4]['value']).encode(t),
                'Bulk Discount': safe_unicode(row[5]['value']).encode(t),
                'Member Discount': safe_unicode(row[6]['value']).encode(t),
                'Physical Address': safe_unicode(row[7]['value']).encode(t),
                'District': safe_unicode(row[8]['value']).encode(t),
                'State': safe_unicode(row[9]['value']).encode(t),
                'City': safe_unicode(row[10]['value']).encode(t),
                'Postal Code': safe_unicode(row[11]['value']).encode(t),
                'Country': safe_unicode(row[12]['value']).encode(t),
                'Postal Address': safe_unicode(row[13]['value']).encode(t),
                'District.': safe_unicode(row[14]['value']).encode(t),
                'State.': safe_unicode(row[15]['value']).encode(t),
                'City.': safe_unicode(row[16]['value']).encode(t),
                'Postal Code.': safe_unicode(row[17]['value']).encode(t),
                'Country.': safe_unicode(row[18]['value']).encode(t),
            })
        report_data = output.getvalue()
        output.close()

        date = datetime.datetime.now().strftime("%Y-%m-%d %H%M")
        setheader = self.request.RESPONSE.setHeader
        setheader('Content-Type', 'text/csv')
        setheader("Content-Disposition",
                  "attachment;filename=\"Clients %s.csv\"" % date)
        self.request.RESPONSE.write(report_data)
