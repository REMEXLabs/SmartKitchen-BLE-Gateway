import logging
import struct

import bluepy.btle


# Exception Classes
class BLEDeviceDuplicatedService(Exception):
    def __init__(self, value):
        self.value = value + ": service already exists"

    def __str__(self):
        return repr(self.value)


class BLEDeviceNoService(Exception):
    def __init__(self, value):
        self.value = value + ": service doesn't exist"

    def __str__(self):
        return repr(self.value)


class BLEServiceDuplicatedUUID(Exception):
    def __init__(self, value):
        self.value = value + ": characteristic already exists"

    def __str__(self):
        return repr(self.value)


# BLEDevice contains services which can be used
class BLEDevice(bluepy.btle.Peripheral):
    def __init__(self, address):
        # NULL Logger
        self.logger = logging.getLogger("NULL")
        self.logger.addHandler(logging.NullHandler())
        self.logger.setLevel(logging.NOTSET)

        # Init Device
        self.logger.debug("{msg}{mac}".format(
            msg="Connecting to ", mac=address))
        bluepy.btle.Peripheral.__init__(self, address)
        self.discoverServices()
        self.services = {}  # all registerd services should be in this list

    def add_service(self, service_id, service):
        if service_id not in self.services:
            self.services[service_id] = service
        else:
            raise BLEDeviceDuplicatedService(service_id)

    def remove_service(self, service_id):
        if service_id in self.services:
            self.services.popitem(service_id)
        else:
            raise BLEDeviceNoService(service_id)

    def set_logger(self, logger_name):
        self.logger = logging.getLogger(logger_name)


# Class to get valid UUIDs through the UUID class from bluepy
class UUID:
    def __init__(self, base, prefix):
        self.base = base
        self.prefix = prefix

    def get_uuid(self, val):
        return bluepy.btle.UUID(self.base % (self.prefix + val))


class Service:
    on = struct.pack("B", 0x01)
    off = struct.pack("B", 0x00)

    def __init__(self, periph, uuid, service_uuid, conf_uuid, data_uuid,
                 service_id):

        self.periph = periph
        self.uuid_generator = uuid
        self.service_uuid = uuid.get_uuid(service_uuid)
        self.conf_uuid = uuid.get_uuid(conf_uuid)
        self.data_uuid = uuid.get_uuid(data_uuid)
        self.service_id = service_id
        self.service = None
        self.config = None
        self.data = None
        self.additional_uuids = {}
        self.additional_characteristics = {}

    def __del__(self):
        self.deactivate()

    def activate(self):
        if self.service is None:
            self.service = self.periph.getServiceByUUID(self.service_uuid)
        if self.config is None:
            self.config = self.service.getCharacteristics(self.conf_uuid)[0]
        if self.data is None:
            self.data = self.service.getCharacteristics(self.data_uuid)[0]

        for key, uuid in self.additional_uuids.iteritems():
            if key not in self.additional_characteristics:
                self.additional_characteristics[key] = \
                    self.service.getCharacteristics(uuid)[0]

        if self.on is not None:
            self.config.write(self.on, withResponse=True)

    def deactivate(self):
        if self.config is not None and self.off is not None:
            self.config.write(self.off)

    def read(self):
        return self.data.read()

    def add_characteristics(self, char_id, uuid):
        if char_id not in self.additional_uuids:
            self.additional_uuids[char_id] = self.uuid_generator.get_uuid(uuid)
        else:
            raise BLEServiceDuplicatedUUID(char_id)

    def log_value(self, logger):
        logger.info("{service}: {value}".format(
            service=self.service_id, value=self.read()))
