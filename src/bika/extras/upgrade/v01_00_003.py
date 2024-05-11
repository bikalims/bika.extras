# -*- coding: utf-8 -*-

from bika.extras.config import PRODUCT_NAME
from bika.extras.config import PROFILE_ID
from bika.extras.config import logger
from bika.extras.setuphandlers import setup_catalogs
from bika.lims import api
from senaite.core.catalog import SENAITE_CATALOG
from senaite.core.upgrade import upgradestep
from senaite.core.upgrade.utils import UpgradeUtils

version = "1.0.3"


@upgradestep(PRODUCT_NAME, version)
def upgrade(tool):
    portal = tool.aq_inner.aq_parent
    setup = portal.portal_setup
    portal = tool.aq_inner.aq_parent
    ut = UpgradeUtils(portal)
    ver_from = ut.getInstalledVersion(PRODUCT_NAME)

    if ut.isOlderVersion(PRODUCT_NAME, version):
        logger.info("Skipping upgrade of {0}: {1} > {2}".format(
            PRODUCT_NAME, ver_from, version))
        return True

    # -------- ADD YOUR STUFF BELOW --------

    setup.runImportStepFromProfile(PROFILE_ID, "workflow")
    setup_catalogs(portal)
    set_up = api.get_setup()
    set_up.reindexObject()
    query = {"portal_type": "Batch"}
    brains = api.search(query, SENAITE_CATALOG)
    for brain in brains:
        obj = brain.getObject()
        obj.reindexObject()

    logger.info("{0} upgraded to version {1}".format(PRODUCT_NAME, version))
    return True
