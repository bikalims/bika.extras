from bika.lims import api
from bika.lims.interfaces import IAddSampleFieldsFlush
from bika.extras.config import logger
from zope.component import getAdapters


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
