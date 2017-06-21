__author__ = 'naveen.krishnan'

import json
from BIMLite.utils import bimlite_util


class BaseDTO(object):
    def dict_for_json(self):
        return self.__dict__

    def to_json(self):
        return json.dumps(self.__dict__)


class MeterConsumption(BaseDTO):
    def __init__(self, meter_number, interval, consumption, meter_reading):
        self.meter_number = meter_number
        self.interval = interval
        self.consumption = consumption
        self.meter_reading = meter_reading


class SiteDTO(BaseDTO):
    def __init__(self, entity_id, latitude, longitude, entity_name):
        self.entity_id= entity_id
        self.latitude = latitude
        self.longitude = longitude
        self.entity_name = entity_name

class DeviceDTO(BaseDTO):
    def __init__(self, entity_id, device_ext_id, latitude, longitude):
        self.entity_id = entity_id
        self.device_ext_id = device_ext_id
        self.latitude = latitude
        self.longitude = longitude

class CylinderDTO(BaseDTO):
    def __init__(self, entity_id,device_entity_id,entity_name, order):
        self.entity_id = entity_id
        self.device_entity_id = device_entity_id
        self.cylinder_name = entity_name
        self.order = order

class CylinderStatusDTO(BaseDTO):
    def __init__(self, status_code,entities_events_map_id,event_record_id, event_recorded_date):
        self.status_code = status_code
        self.entities_events_map_id = entities_events_map_id
        self.event_record_id = event_record_id
        self.event_recorded_date = event_recorded_date
