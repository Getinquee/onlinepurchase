__author__ = 'kamakhya'

import logging
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from BIMLite.src.handlers.bimlite_request_handler import BIMLiteRequestHandler

class BIMLiteSiteHandler(BIMLiteRequestHandler):
    """
    Class responsible for handling the site API  call '/'.
    Displays  site details in json format for  BIMLite application
    """

    def __init__(self,application, request, **kwargs):
        super(BIMLiteSiteHandler, self).__init__(application, request, **kwargs)
        self.log = logging.getLogger(__name__)

    def initialize(self, site_service):
        self.site_service = site_service

    @tornado.web.asynchronous
    def get(self):
        """
        API : http://<ip>:<port>/
        The get http request handler for the sites API  call '/'.
        The result of the page is  site details in json format for BIMLite application.
        """
        try:
            status_code, message = self.site_service.get_sites()
            self.set_status(status_code)
            self.write(message)
        except:
            self.write('The request processing has failed because of an unknown error, exception or failure')
            self.set_status(500)
        finally:
            self.finish()