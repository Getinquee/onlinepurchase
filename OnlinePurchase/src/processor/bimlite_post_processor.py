__author__ = 'naveen.krishnan'

import logging

from BIMLite.src.processor.reorder_level_processor import ReorderLevelProcessor

from BIMLite.src.processor.inventory_critical_processor import InventoryCriticalProcessor
from BIMLite.config import config

class BIMLitePostProcessor(object):
    """
    This class is responsible for post processing the data once the status data from the device are persisted.
     Post processing may contain
     1. Sending status notification on each status to the user
     2. Check and send re-order level notification comparing with reorder configuration
     3. Check and send inventory control notification based on the inventory control configuration
      All of the above configurations are configurable in the config.ini file
    """

    def __init__(self, bimlite_data_service, entity_status, notification_processor):
        self.log = logging.getLogger(__name__)
        self.bimlite_data_service = bimlite_data_service
        self.entity_status = entity_status
        self.notification_processor = notification_processor

    def execute(self, data):
        try:
            # Get the entity / device id from the device table
            device_id = self.bimlite_data_service.get_device_id(data['device_ext_id'])
            # Only one port id is sent as part of the device_capability_ids for BIMLite
            capability_port = data['device_capability_ids'][0]
            # Get the latest devices' cylinders statuses for processing
            latest_device_statuses = self.notification_processor.device_status_processor.get_latest_device_statuses(device_id)

            # Status notification for each status received from the device
            if config.send_status_notification():
                self.log.info('Status notification check started')
                self.notification_processor.notify_device_status(capability_port, latest_device_statuses)
                self.log.info('Status notification check finished')

            # Status notification for reorder level as per the cylinder status configuration
            if config.reorder_level_notification_enabled(device_id):
                self.log.info('Re-order level notification check started')
                reorder_level_identified = ReorderLevelProcessor(config).reorder_level_identified(device_id, latest_device_statuses)
                if reorder_level_identified:
                    capability_port = config.get_device_capability_port_reorder(device_id)
                    self.notification_processor.notify_device_status(capability_port, latest_device_statuses)
                self.log.info('Re-order level notification check finished')

            # Status notification for inventory critical as per the cylinder status configuration
            if config.inventory_critical_notification_enabled(device_id):
                self.log.info('Inventory critical notification check started')
                ventory_critical_identified = InventoryCriticalProcessor(config).inventory_critical_identified(
                    device_id, latest_device_statuses)
                if ventory_critical_identified:
                    capability_port = config.get_device_capability_port_inventory_critical(device_id)
                    self.notification_processor.notify_device_status(capability_port, latest_device_statuses)
                self.log.info('Inventory critical notification check finished')

            return True
        except Exception:
            return False
