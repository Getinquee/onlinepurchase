__author__ = 'naveen.krishnan'

from collections import defaultdict
import json

from BIMLite.src.bimlite_constants import StatusShortcuts


class InventoryCriticalProcessor(object):
    """ This class is responsible for checking whether the data passed is eligible for raising inventory critical
    notification.
     Once the data found to be a candidate for inventory critical notification, the user is notified on the same.
    """

    def __init__(self, config):
        self.config = config

    def inventory_critical_identified(self, device_id, cylinder_statuses):
        reorder_config = self.config.get_inventory_critical_for_device(device_id)
        reorder_conf = json.loads(reorder_config)
        reorder_conf = {k: v for k, v in reorder_conf.items() if v}  # Filter out 0 values
        status_dict = defaultdict(int)
        if reorder_config:
            cylinder_statuses = cylinder_statuses[2::2]
            for cylinder_status in cylinder_statuses:
                code = getattr(StatusShortcuts, cylinder_status.status_code)
                status_dict[code] += 1
            status_dict = {k: v for k, v in status_dict.items() if k != 'SV'}  # Filter out SV status.
            # Only the cylinders status Full, Inuse and Empty are checked - SV is ignored.
            if reorder_conf == status_dict:
                return True
        return False
