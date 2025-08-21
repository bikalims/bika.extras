# -*- coding: utf-8 -*-

from Products.CMFPlone.utils import safe_unicode
from collections import OrderedDict
from zope.component import getAdapters

from bika.extras.config import _
from bika.extras.config import logger
from bika.lims import api
from bika.lims.interfaces import IAddSampleFieldsFlush


from bika.lims.interfaces import IAddSampleRecordsValidator


def get_client_queries(self, obj, record=None):
    """Returns the filter queries to be applied to other fields based on
    both the Client object and record
    """
    # UID of the client
    uid = api.get_uid(obj)

    # catalog queries for UI field filtering
    queries = {
        "Contact": {
            "getParentUID": [uid]
        },
        "CCContact": {
            "getParentUID": [uid]
        },
        "SamplePoint": {
            "getClientUID": [uid, ""],
        },
        "Template": {
            "getClientUID": [uid, ""],
        },
        "Profiles": {
            "getClientUID": [uid, ""],
        },
        "Specification": {
            "getClientUID": [uid, ""],
        },
        "Sample": {
            "getClientUID": [uid],
        },
        "Batch": {
            "getClientUID": [uid, ""],
        },
        "PrimaryAnalysisRequest": {
            "getClientUID": [uid, ""],
        }
    }

    return queries


def get_sampletype_queries(self, obj, record=None):
    """Returns the filter queries to apply to other fields based on both
    the SampleType object and record
    """
    queries = {}

    return queries


def ajax_get_flush_settings(self):
    """Returns the settings for fields flush

    NOTE: We automatically flush fields if the current value of a dependent
          reference field is *not* allowed by the set new query.
          -> see self.ajax_is_reference_value_allowed()
          Therefore, it makes only sense for non-reference fields!
    """
    flush_settings = {
        "Client": [
        ],
        "Contact": [
        ],
        "PrimarySample": [
            "EnvironmentalConditions",
        ]
    }

    # Maybe other add-ons have additional fields that require flushing
    for name, ad in getAdapters((self.context,), IAddSampleFieldsFlush):
        logger.info("Additional flush settings from {}".format(name))
        additional_settings = ad.get_flush_settings()
        for key, values in additional_settings.items():
            new_values = flush_settings.get(key, []) + values
            flush_settings[key] = list(set(new_values))

    return flush_settings


def ajax_submit(self):
    """Create samples and redirect to configured actions
    """
    # Check if there is the need to display a confirmation pane
    confirmation = self.check_confirmation()
    if confirmation:
        return {"confirmation": confirmation}

    # Get the maximum number of samples to create per record
    max_samples_record = self.get_max_samples_per_record()

    # Get AR required fields (including extended fields)
    fields = self.get_ar_fields()
    required_keys = [field.getName() for field in fields if field.required]

    # extract records from request
    records = self.get_records()

    fielderrors = {}
    errors = {"message": "", "fielderrors": {}}

    valid_records = []

    # Validate required fields
    for num, record in enumerate(records):

        # Extract file uploads (fields ending with _file)
        # These files will be added later as attachments
        file_fields = filter(lambda f: f.endswith("_file"), record)
        uploads = map(lambda f: record.pop(f), file_fields)
        attachments = [self.to_attachment_record(f) for f in uploads]

        # Required fields and their values
        required_values = [record.get(key) for key in required_keys]
        required_fields = dict(zip(required_keys, required_values))

        # Client field is required but hidden in the AR Add form. We remove
        # it therefore from the list of required fields to let empty
        # columns pass the required check below.
        if record.get("Client", False):
            required_fields.pop("Client", None)

        # Check if analyses are required for sample registration
        if not self.analyses_required():
            required_fields.pop("Analyses", None)

        # Contacts get pre-filled out if only one contact exists.
        # We won't force those columns with only the Contact filled out to
        # be required.
        contact = required_fields.pop("Contact", None)

        # None of the required fields are filled, skip this record
        if not any(required_fields.values()):
            continue

        # Re-add the Contact
        required_fields["Contact"] = contact

        # Check if the contact belongs to the selected client
        contact_obj = api.get_object(contact, None)
        if not contact_obj:
            fielderrors["Contact"] = _("No valid contact")
        else:
            parent_uid = api.get_uid(api.get_parent(contact_obj))
            if parent_uid != record.get("Client"):
                msg = _("Contact does not belong to the selected client")
                fielderrors["Contact"] = msg

        if not record['CCContact'] and contact_obj:
            cc_contacts = contact_obj.getCCContact()
            if cc_contacts:
                record["CCContact"] = [cc.UID() for cc in cc_contacts]

        # Check if the number of samples per record is permitted
        num_samples = self.get_num_samples(record)
        if num_samples > max_samples_record:
            msg = _(u"error_analyssirequest_numsamples_above_max",
                    u"The number of samples to create for the record "
                    u"'Sample ${record_index}' (${num_samples}) is above "
                    u"${max_num_samples}",
                    mapping={
                        "record_index": num+1,
                        "num_samples": num_samples,
                        "max_num_samples": max_samples_record,
                    })
            fielderrors["NumSamples"] = self.context.translate(msg)

        # Missing required fields
        missing = [f for f in required_fields if not record.get(f, None)]

        # Handle fields from Service conditions
        for condition in record.get("ServiceConditions", []):
            if condition.get("type") == "file":
                # Add the file as an attachment
                file_upload = condition.get("value")
                att = self.to_attachment_record(file_upload)
                if att:
                    # Add the file as an attachment
                    att.update({
                        "Service": condition.get("uid"),
                        "Condition": condition.get("title"),
                    })
                    attachments.append(att)
                # Reset the condition value
                filename = file_upload and file_upload.filename or ""
                condition.value = filename

            if condition.get("required") == "on":
                if not condition.get("value"):
                    title = condition.get("title")
                    if title not in missing:
                        missing.append(title)

        # If there are required fields missing, flag an error
        for field in missing:
            fieldname = "{}-{}".format(field, num)
            label = self.get_field_label(field) or field
            msg = self.context.translate(_("Field '{}' is required"))
            fielderrors[fieldname] = msg.format(label)

        # Process and validate field values
        valid_record = dict()
        tmp_sample = self.get_ar()
        for field in fields:
            field_name = field.getName()
            field_value = record.get(field_name)
            if field_value in ['', None]:
                continue

            # process the value as the widget would usually do
            process_value = field.widget.process_form
            value, msgs = process_value(tmp_sample, field, record)
            if not value:
                continue

            # store the processed value as the valid record
            valid_record[field_name] = value

            # validate the value
            error = field.validate(value, tmp_sample)
            if error:
                field_name = "{}-{}".format(field_name, num)
                fielderrors[field_name] = error

        # add the attachments to the record
        valid_record["attachments"] = filter(None, attachments)

        # append the valid record to the list of valid records
        valid_records.append(valid_record)

    # return immediately with an error response if some field checks failed
    if fielderrors:
        errors["fielderrors"] = fielderrors
        return {'errors': errors}

    # do a custom validation of records. For instance, we may want to rise
    # an error if a value set to a given field is not consistent with a
    # value set to another field
    validators = getAdapters((self.request, ), IAddSampleRecordsValidator)
    for name, validator in validators:
        validation_err = validator.validate(valid_records)
        if validation_err:
            # Not valid, return immediately with an error response
            return {"errors": validation_err}

    # create the samples
    try:
        samples = self.create_samples(valid_records)
    except Exception as e:
        errors["message"] = str(e)
        logger.error(e, exc_info=True)
        return {"errors": errors}

    # We keep the title to check if AR is newly created
    # and UID to print stickers
    ARs = OrderedDict()
    for sample in samples:
        ARs[sample.Title()] = sample.UID()

    level = "info"
    if len(ARs) == 0:
        message = _('No Samples could be created.')
        level = "error"
    elif len(ARs) > 1:
        message = _('Samples ${ARs} were successfully created.',
                    mapping={'ARs': safe_unicode(', '.join(ARs.keys()))})
    else:
        message = _('Sample ${AR} was successfully created.',
                    mapping={'AR': safe_unicode(ARs.keys()[0])})

    # Display a portal message
    self.context.plone_utils.addPortalMessage(message, level)

    return self.handle_redirect(ARs.values(), message)
