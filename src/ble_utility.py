import struct
import logging

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


class BLELogger:

    def __init__(self, ch_lvl,  file_lvl, log=None):
        # TODO: Maybe check for wrong logging levels?
        if log:
            # Init Logger
            self.logger = logging.getLogger("ble_logger")
            self.logger.setLevel(logging.WARNING)

            # Console Handler:
            ch_handler = logging.StreamHandler
            ch_handler.setLevel(ch_lvl)
            ch_format = logging.Formatter("%(levelname)s - %(message)s")
            ch_handler.setFormatter(ch_format)
            self.logger.addHandler(ch_handler)

            # File Handler
            file_handler = logging.FileHandler("ble_utility.log", "w", "utf-8")
            file_handler.setLevel(file_lvl)
            file_format = logging.Formatter(
                "%(asctime)s - %(levelname)s - %(message)s")
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)

    def __del__(self):
        del(self.logger)


# BLEDevice contains services which can be used
class BLEDevice(bluepy.btle.Peripheral):

    def __init__(self, address, log=False, ch_lvl=logging.ERROR,
                 file_lvl=logging.DEBUG):
        # Init Logger
        if log:
            BLELogger(ch_lvl, file_lvl, log)

        # Init Device
        logging.Debug("{msg}{mac}".format(msg="Connecting to ", mac=address))
        bluepy.btle.Peripheral.__init__(self, address)
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

    def __init__(self, periph, service_uuid, conf_uuid, data_uuid):
        self.periph = periph
        self.service = None
        self.config = None
        self.data = None
        self.service_uuid = service_uuid
        self.conf_uuid = conf_uuid
        self.data_uuid = data_uuid
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

        self.config.write(self.on, withResponse=True)

    def deactivate(self):
        if self.config is not None:
            self.config.write(self.off)

    def read(self):
        return self.data.read()

    def add_characteristics(self, char_id, uuid):
        if char_id not in self.additional_uuids:
            self.additional_uuids[char_id] = uuid
        else:
            raise BLEServiceDuplicatedUUID(char_id)
