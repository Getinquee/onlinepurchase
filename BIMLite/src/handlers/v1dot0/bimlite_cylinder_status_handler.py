__author__ = 'kamakhya'

import logging
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from BIMLite.src.handlers.bimlite_request_handler import BIMLiteRequestHandler

class BIMLiteCylinderStatusHandler(BIMLiteRequestHandler):
    """
    Class responsible for handling the cylinderStatus API  call '/'.
    Displays  cylinderStatus  for the device in json format for  BIMLite application
    """

    def __init__(self,application, request, **kwargs):
        super(BIMLiteCylinderStatusHandler, self).__init__(application, request, **kwargs)
        self.log = logging.getLogger(__name__)

    def initialize(self, cylinder_status_service):
        self.cylinder_status_service = cylinder_status_service

    @tornado.web.asynchronous
    def get(self, device_id):
        """
        API : http://<ip>:<port>/
        The get http request handler for the cylinder API  call '/'.
        The result of the page is  cylinder details in json format for BIMLite application.
        """
        try:
            status_code, message = self.cylinder_status_service.get_cylinder_status(int(device_id))
            self.set_status(status_code)
            self.write(message)
        except:
            self.write('The request processing has failed because of an unknown error, exception or failure')
            self.set_status(200)
        finally:
            self.finish()