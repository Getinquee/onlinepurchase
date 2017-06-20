__author__ = 'naveen.krishnan'

import calendar
from datetime import datetime

def date_time_to_epoch(datetime):
    # Takes the date time object returned from database and converts into UTC epoch to send as json response
    return calendar.timegm(datetime.utctimetuple())

def epoch_to_date_time(epoch):
    # Takes the date time object from client in epoch format and converts into UTC time
    return datetime.utcfromtimestamp(float(epoch))