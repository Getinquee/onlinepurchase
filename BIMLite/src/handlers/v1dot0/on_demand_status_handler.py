__author__ = 'naveen.krishnan'

import logging
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from BIMLite.config import config
from BIMLite.src.handlers.bimlite_request_handler import BIMLiteRequestHandler

class BIMLiteOndemandStatusHandler(BIMLiteRequestHandler):
    """
    Class responsible for handling the API call which is responsible for sending latest status of device
    when asked by the consumer by sending SMS to McWane specified GVN.
    The latest status received by the BIMLite will be fetched and notified to the customer.
    This feature will be enhanced by the status being requested from the device in future.
    """

    def __init__(self, application, request, **kwargs):
        super(BIMLiteOndemandStatusHandler, self).__init__(application, request, **kwargs)
        self.log = logging.getLogger(__name__)

    def initialize(self, notification_processor):
        self.notification_processor = notification_processor

    @tornado.web.asynchronous
    def get(self):
        """
        API : http://<ip>:<port>/device/status/([A-Za-z0-9]+)
        device_ext_id - the external device id is passed to the url and the notification message would be sent to the
        list of persons whose mobile numbers are already configured.
        """
        try:
            # TODO give the public url
            # TODO get user and pass from url

            if self._is_authentic_user():
                self.log.info('Started processing of on demand status')
                # Getting the device id from the database passing in the device external id
                device_external_id = 'bimlite1'
                device_id = self.notification_processor.device_status_processor.get_device_id(device_external_id)

                # Getting the capability_port from the device id from config file
                capability_port = config.get_device_capability_port(device_id)

                self.notification_processor.get_latest_device_statuses_and_notify(device_id, capability_port)
                self.log.info('Completed processing of on demand status')
                self.write('On demand status notified')
            else:
                self.log.info('Authentication failed for getting on demand status')
                self.set_status(401)
                self.write('Authentication failed for getting on demand status')
        except Exception:
            logging.exception('Error establishing session with the server')
        finally:
            self.finish()

    def _is_authentic_user(self):
        authorization_token = self.request.headers.get('Authorization')
        if authorization_token:
            usercredentials = authorization_token.split('Basic ')[1].split(':')
            username = usercredentials[0]
            password = usercredentials[1]
            return config.is_authentic_user(username, password)
        else:
            return False
