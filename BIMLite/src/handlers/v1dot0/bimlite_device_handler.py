__author__ = 'kamakhya'

import logging
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from BIMLite.src.handlers.bimlite_request_handler import BIMLiteRequestHandler

class BIMLiteDeviceHandler(BIMLiteRequestHandler):
    """
    Class responsible for handling the device API  call '/'.
    Displays  device details for the site in json format for  BIMLite application
    """

    def __init__(self,application, request, **kwargs):
        super(BIMLiteDeviceHandler, self).__init__(application, request, **kwargs)
        self.log = logging.getLogger(__name__)

    def initialize(self, device_service):
        self.device_service = device_service

    @tornado.web.asynchronous
    def get(self, site_id):
        """
        API : http://<ip>:<port>/
        The get http request handler for the device API  call '/'.
        The result of the page is  device details in json format for BIMLite application.
        """
        try:
            status_code, message = self.device_service.get_devices(int(site_id))
            self.set_status(status_code)
            self.write(message)
        except:
            self.write('The request processing has failed because of an unknown error, exception or failure')
            self.set_status(200)
        finally:
            self.finish()