# -*- coding: utf-8 -*-

from string import Template
from collections import OrderedDict

from Products.CMFPlone.utils import safe_unicode
from Products.PlonePAS.plugins.ufactory import PloneUser
from Products.PlonePAS.tools.memberdata import MemberData

from bika.extras.config import _
from bika.lims import api
from senaite.core.catalog import SAMPLE_CATALOG
from bika.lims.api.mail import compose_email
from bika.lims.api.mail import is_valid_email_address
from bika.lims.interfaces import IContact
from bika.lims.utils import get_link
from bika.lims.utils import get_link_for


def after_receive(sample):
    """Method triggered after "export" transition for AR in order to transition
    the batch if all AR's within it have been exported.
    """
    notify_client_contacts(sample)


def notify_client_contacts(sample):
    """Checks if all samples have been received and notifies
       client contacts by email
    """
    send = can_send_notification(sample)
    if send:
        batch = sample.getBatch()
        samples = batch.getAnalysisRequests()
        send_received_email(samples)
        batch.NotifiedSamplesReceived = True
        batch.reindexObject()
        message = _("Sent email for ")
        message = _(
            "Sent email for receiving samples for ${batch_id}",
            mapping={"batch_id": api.get_id(batch)},
        )
        sample.plone_utils.addPortalMessage(message, "info")


def can_send_notification(sample):
    """Returns whether the batch email has been sent for received samples
    """
    batch = sample.getBatch()
    if batch.Schema()["NotifiedSamplesReceived"].getAccessor(batch)():
        return False

    query = {
        "getBatchUID": batch.UID(),
        "portal_type": "AnalysisRequest",
        "getDateReceived": {"query": "", "range": "min"},
    }
    brains = api.search(query, SAMPLE_CATALOG)
    if not brains:
        return False

    samples = batch.getAnalysisRequests()
    if len(samples) == len(brains):
        # all samples have been received
        return True


def send_received_email(samples):
    """Sends an email notification to sample's client contact if the sample
    passed in has a retest associated
    """
    try:
        email_message = get_invalidation_email(samples)
        host = api.get_tool("MailHost")
        host.send(email_message, immediate=True)
    except Exception as err_msg:
        batch = samples[0].getBatch()
        message = _(
            "Cannot send email for receiving samples for ${batch_id} : ${error}",
            mapping={
                "batch_id": api.get_id(batch),
                "error": safe_unicode(err_msg),
            },
        )
        samples[0].plone_utils.addPortalMessage(message, "warning")


def get_invalidation_email(samples):
    """Returns the sample invalidation MIME Message for the sample
    """
    managers = api.get_users_by_roles("LabManager")
    contacts = []
    for sample in samples:
        if sample.getContact() not in contacts:
            contacts.append(sample.getContact())
        for cc_contact in sample.getCCContact():
            if cc_contact not in contacts:
                contacts.append(cc_contact)
    recipients = managers + contacts
    recipients = filter(None, map(get_email_address, recipients))
    # Get the recipients
    recipients = list(OrderedDict.fromkeys(recipients))

    if not recipients:
        for sample in samples:
            sample_id = api.get_id(sample)
            raise ValueError("No valid recipients for {}".format(sample_id))

    # TODO: Get Batch and see if the unique batch
    batch = samples[0].getBatch()
    # Compose the email
    subject = samples[0].translate(
        _(
            "Samples received for case: ${batch_id}",
            mapping={"batch_id": api.get_id(batch)},
        )
    )

    setup = api.get_setup()
    lab_name = setup.laboratory.Title()
    lab_email = setup.laboratory.getEmailAddress()
    lab_address = setup.laboratory.getPrintAddress()
    number_of_samples = len(samples)
    client_name = batch.getClient().Title() if batch.getClient() else ""
    batch_id = api.get_id(batch)
    batch_url = batch.absolute_url()
    client_batch_id = batch.getClientBatchID()
    rseb = setup.Schema()["ReceivedSamplesEmailBody"].getAccessor(setup)()
    body = Template(rseb)
    body = body.safe_substitute(
        {
            "case_id": get_link(batch_url, value=batch_id),
            "case_title": get_link_for(batch, csrf=False),
            "case_number": get_link(batch_url, value=client_batch_id),
            "client_name": client_name,
            "lab_name": lab_name,
            "lab_address": "<br/>".join(lab_address),
            "number_of_samples": number_of_samples,
            "recipients": ", ".join([i.getFullname() for i in contacts]),
        }
    )

    return compose_email(
        from_addr=lab_email,
        to_addr=recipients,
        subj=subject,
        body=body,
        html=True,
    )


def get_email_address(contact_user_email):
    """Returns the email address for the contact, member or email
    """
    if is_valid_email_address(contact_user_email):
        return contact_user_email

    if IContact.providedBy(contact_user_email):
        contact_email = contact_user_email.getEmailAddress()
        return get_email_address(contact_email)

    if isinstance(contact_user_email, MemberData):
        contact_user_email = contact_user_email.getUser()

    if isinstance(contact_user_email, PloneUser):
        # Try with the contact's email first
        contact = api.get_user_contact(contact_user_email)
        contact_email = get_email_address(contact)
        if contact_email:
            return contact_email

        # Fallback to member's email
        user_email = contact_user_email.getProperty("email")
        return get_email_address(user_email)

    return None
