__author__ = 'naveen.krishnan'

import logging


class DeviceStatusProcessor(object):
    def __init__(self, bimlite_operations):
        self.log = logging.getLogger(__name__)
        self.bimlite_operations = bimlite_operations

    def get_latest_device_statuses(self, device_id):
        """
        Gets the list of cylinder statuses for the device including device status.
        :return: latest_device_statuses - list of statuses
        """
        try:
            self.log.info('Fetching latest device statuses started')
            latest_device_statuses = self.bimlite_operations.get_latest_device_status(device_id)
            self.log.info('Fetching latest device statuses completed')
            return latest_device_statuses
        except:
            raise

    def get_device_id(self, device_external_id):
        """
        Gets the device external id and returns the device id.
        :return: device id - the primary key id from the database.
        """
        try:
            self.log.info('Fetching device id started')
            device_id = self.bimlite_operations.get_device_id(device_external_id)
            self.log.info('Fetching device id completed')
            return device_id
        except:
            raise
