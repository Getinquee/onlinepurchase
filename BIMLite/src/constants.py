__author__ = 'naveen.krishnan'


class Status(object):
    ON = 'on'
    OFF = 'off'
    OPEN = 'open'
    CLOSE = 'close'
    VALVE_ON = 'valveon'
    VALVE_OFF = 'valveoff'
    ACK_PRESSED = 'ackpressed'
    ACK_NOT_PRESSED = 'acknotpressed'
    CAPACITY_EMPTY = 'capacityempty'
    CAPACITY_IN_USE = 'capacityinuse'
    CAPACITY_SV = 'capacitysv'
    CAPACITY_FULL = 'capacityfull'
    LOW_GAS_FLOW = 'lowgasflow'
    HIGH_GAS_FLOW = 'highgasflow'
    AUTO_MODE = 'automode'
    MANUAL_MODE = 'manualmode'


class StatusShortcuts(object):
    valveon = 'O'
    valveoff = 'C'
    capacityempty = 'E'
    capacityinuse = 'I'
    capacitysv = 'SV'
    capacityfull = 'F'
    lowgasflow = 'LG'
    highgasflow = 'HG'
    automode = 'AM'
    manualmode = 'MM'