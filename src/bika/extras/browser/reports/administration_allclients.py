# -*- coding: utf-8 -*-

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
        headings['subheader'] = _(
            "All Clients")

        count_all = 0

        query = {'portal_type': 'Client',
                 'is_active': True,
                 'sort_order': 'reverse'}

        # and now lets do the actual report lines
        formats = {'columns': 19,
                   'col_heads': [_('Client'),
                                 _('Client ID'),
                                 _('Email Address'),
                                 _('CC Emails'),
                                 _('Phone Number'),
                                 _('Bulk Discount'),
                                 _('Member Discount'),
                                 _('Physical Address'),
                                 _('District'),
                                 _('State'),
                                 _('City'),
                                 _('Postal code'),
                                 _('Country'),
                                 _('Postal Address'),
                                 _('District'),
                                 _('State'),
                                 _('City'),
                                 _('Postal code'),
                                 _('Country'),
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
            dataitem = {'value': obj.PhysicalAddress.get("address")}
            dataline.append(dataitem)
            dataitem = {'value': obj.PhysicalAddress.get("district")}
            dataline.append(dataitem)
            dataitem = {'value': obj.PhysicalAddress.get("state")}
            dataline.append(dataitem)
            dataitem = {'value': obj.PhysicalAddress.get("city")}
            dataline.append(dataitem)
            dataitem = {'value': obj.PhysicalAddress.get("zip")}
            dataline.append(dataitem)
            dataitem = {'value': obj.PhysicalAddress.get("country")}
            dataline.append(dataitem)
            dataitem = {'value': obj.PostalAddress.get("address")}
            dataline.append(dataitem)
            dataitem = {'value': obj.PostalAddress.get("district")}
            dataline.append(dataitem)
            dataitem = {'value': obj.PostalAddress.get("state")}
            dataline.append(dataitem)
            dataitem = {'value': obj.PostalAddress.get("city")}
            dataline.append(dataitem)
            dataitem = {'value': obj.PostalAddress.get("zip")}
            dataline.append(dataitem)
            dataitem = {'value': obj.PostalAddress.get("country")}
            dataline.append(dataitem)

            datalines.append(dataline)

            count_all += 1

        # table footer data
        footlines = []
        footline = []
        footitem = {'value': _('All Clients'),
                    'colspan': 18,
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
