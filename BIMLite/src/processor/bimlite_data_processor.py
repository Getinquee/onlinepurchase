__author__ = 'naveen.krishnan'

import logging
from datetime import datetime
from collections import OrderedDict

from BIMLite.src.bimlite_constants import Status
from BIMLite.src.db.model import EventRecord, EventHistory
from BIMLite.src.processor import bimlite_post_processor


class BIMLiteDataProcessor(object):
    def __init__(self, bimlite_data_service, entity_status, notification_processor):
        self.log = logging.getLogger(__name__)
        self.bimlite_data_service = bimlite_data_service
        self.entity_status = entity_status
        self.notification_processor = notification_processor

    def process_bimlite_data(self, data):
        """Processes the BIM Lite data logs .
        Get the bim lite status logs from the device, process the data and construct object to persist into the database
        :param data
        :type json - data from the message queue written from the MIGDAP layer
        :return the status True / False to acknowledge back to the message queue.
        """
        try:
            self.log.info('Started processing of BIMLite data')
            process_status = self._parse_bimlite_data_and_persist(data)
            if process_status:
                bimlite_post_processor.BIMLitePostProcessor(self.bimlite_data_service, self.entity_status,
                                                            self.notification_processor).execute(data)
            return process_status
        except Exception:
            self.log.exception('Error processing BIMLite data')
            return None

    def _parse_bimlite_data_and_persist(self, bim_lite_data):
        """
        The bim_lite_data json is parsed in this method and the data values are read.
          The data values are sent from the devices in hex format, which is converted into bytes (8 bits), each bit
          representing a status of predefined in the device. Each of the status is then persisted against the DB.
        :param bim_lite_data: the json data.
        :return: boolean True / False state of the parse and persist.
        """

        device_ext_id = bim_lite_data['device_ext_id']
        capability_port = bim_lite_data['monitored_port_ids'][0]
        time_reference = int(bim_lite_data['time_reference'])
        data_values_dict = bim_lite_data['data_values']

        # Statuses are fetched once from the application bootstrap state and used till the application life ends.
        # If any case the statuses are not loaded it is re-generate using db call below, which is edge case.
        if self.entity_status is None:
            self.entity_status = self.bimlite_data_service.get_all_statuses()

        """All of the entities events map ids are fetched from the database for persisting in the records table
        referencing the entities events maps ids.
        """
        entities_events_map_ids = self._get_all_entities_events_ids(device_ext_id, capability_port)

        """Based on the number of time stamp data available in the data records
        loop in through the no of times of the timestamp's data available, which will process each time record set and
        construct the db model object and sends to the crud layer for persisting
        """
        data_values = sorted(data_values_dict.keys())
        for time_delta in data_values:
            # Always we get only one data values since we get only one port's value from BIMLite device
            status_values = data_values_dict[time_delta][0]
            status_values_list = status_values.split(',')
            event_time = time_reference + int(time_delta)
            event_histories = []
            for index, status_value in enumerate(status_values_list):
                # First status will always be for the device and remaining will be for the cylinders
                entities_events_map_id = entities_events_map_ids[index]
                if index == 0:
                    event_histories = self._get_entity_histories(SiteStatus, entities_events_map_id, status_value,
                                                                 self.entity_status)
                else:
                    event_histories = event_histories + \
                                      self._get_entity_histories(CylinderStatus, entities_events_map_id, status_value,
                                                                 self.entity_status)

            """Build the event_record object with one entry. Each date-time record will have one record in the event
             record table and corresponding id is referred in the event history table with individual statuses.
             """
            event_record = EventRecord()
            event_record.recorded_date = self._epoch_to_date_time(event_time)
            event_record.created_date = datetime.utcnow()

            """Build the reference object with multiple entries for each status.
            One event record will have multiple event histories for persistence.
            """
            self.bimlite_data_service.save_event_records_and_history(event_record, event_histories)

        return True

    def _get_all_entities_events_ids(self, device_ext_id, capability_port):
        all_entities_events_map_ids = OrderedDict()

        # - Get the event id from the events table
        event_id = self.bimlite_data_service.get_event_id(capability_port)

        # - Get the entity / device id from the device table
        device_id = self.bimlite_data_service.get_device_id(device_ext_id)
        # - Get the entities_events_map_id from the device_id(entity_id in db) and the port_id(event)
        device_entities_events_map_id = self.bimlite_data_service.get_entities_events_map(device_id, event_id)

        all_entities_events_map_ids[device_id] = device_entities_events_map_id

        # - Get the entity / cylinder id from the cylinder table
        cylinder_ids = self.bimlite_data_service.get_cylinder_ids(device_id)
        # - Get the entities_events_map_id from the device_id(entity_id in db) and the port_id(event)
        cylinder_entities_events_map_ids = []
        for cylinder_id in cylinder_ids:
            cylinder_entities_events_map_ids.append(
                self.bimlite_data_service.get_entities_events_map(cylinder_id, event_id))

        """ Once the entities events ids are fetched from the DB, the data is constructed into a dict, where the key is
        the entity id and the corresponding events mapping id is the value.
        """
        for index, cylinder_id in enumerate(cylinder_ids):
            all_entities_events_map_ids[cylinder_id] = cylinder_entities_events_map_ids[index]

        return list(all_entities_events_map_ids.values())

    def _get_entity_histories(self, clazz, entities_events_map_id, status, status_dict):
        """
        Process the data
        - hex to bytes conversion
        - bytes to bit parsing. Each bit carries a status.
        - Each bit status value is got from the corresponding [Site/ Cylinder]status classes.
        - The bits status are then put in a list for persisting in the DB.
        """
        site_status_binary_code = '{:08b}'.format(int(status, 16))
        device_statuses_list = clazz.get_statuses(site_status_binary_code)
        event_histories = []
        for device_status in device_statuses_list:
            event_history = EventHistory()
            event_history.status_id = status_dict[device_status]
            event_history.entities_events_map_id = entities_events_map_id
            event_histories.append(event_history)
        return event_histories

    def _epoch_to_date_time(self, epoch):
        # Takes the date time object in epoch format and converts into UTC time
        return datetime.utcfromtimestamp(float(epoch))


class SiteStatus(object):
    @staticmethod
    def _get_status(index, binary_code):
        site_statuses = [
            [Status.AUTO_MODE, Status.MANUAL_MODE],
            [Status.LOW_GAS_FLOW, Status.HIGH_GAS_FLOW]
        ]

        if index >= 2:  # bit reserved in f/w for future use, so skipping the processing
            return None
        return site_statuses[index][int(binary_code)]

    @staticmethod
    def get_statuses(status_binary_code):

        """ This function gets the statuses in binary form, parsed and then sends the list of corresponding
        statuses to be inserted into the database.
        :param status_binary_code:
        :return: list of statuses
        """
        site_status = str(status_binary_code)
        site_statuses = []
        for index, status in enumerate(reversed(site_status)):
            status = SiteStatus._get_status(index, status)
            if status is None:
                break
            site_statuses.append(status)
        return site_statuses


class CylinderStatus(object):
    @staticmethod
    def _get_status(index, binary_code):
        statuses = [[],
                    # Empty item since cylinders status are sent using  both the last bits which is handled with next item.
                    [[Status.CAPACITY_EMPTY, Status.CAPACITY_IN_USE], [Status.CAPACITY_SV, Status.CAPACITY_FULL]],
                    [Status.VALVE_OFF, Status.VALVE_ON]
                    ]

        if index == 1:  # Since cylinders initial statuses occupies two bits, parsing here
            return statuses[index][int(binary_code[0])][int(binary_code[1])]

        if index >= 3:  # bit reserved in f/w for future use so skipping the processing
            return None

        return statuses[index][int(binary_code)]

    @staticmethod
    def get_statuses(status_binary_code):

        """ This function gets the statuses in binary form, parsed and then sends the list of corresponding
        statuses to be inserted into the database.
        :param status_binary_code:
        :return: list of statuses
        """
        site_status = str(status_binary_code)
        site_statuses = []
        temp_status = ''
        for index, status in enumerate(reversed(site_status)):
            if index == 0:
                temp_status = status
                continue
            elif index == 1:
                status = status + temp_status
            status = CylinderStatus._get_status(index, status)
            if status is None:
                break
            site_statuses.append(status)
        return site_statuses
