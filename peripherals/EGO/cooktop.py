import ble_utility
import struct



'''
Vendor & Device information
'''

class Vendor(ble_utility.Service):

    def __init__(self, periph):
        uuid_generator = ble_utility.UUID()

        self.service_uuid = uuid_generator.get_uuid(0x180A)
        self.config_uuid = None
        self.data_uuid = uuid_generator.get_uuid(0x2A29)
        self.period_uuid = None
        self.on = None  # does not need to be switched on!

        ble_utility.Service.__init__(self, periph, uuid_generator, self.service_uuid,
                                 self.config_uuid,
                                 self.data_uuid, "vendor")

    def read(self):
        # returns the vendor name as a string
        val = self.data.read()
        return val


class Device(ble_utility.Service):

    def __init__(self, periph):
        uuid_generator = ble_utility.UUID()

        self.service_uuid = uuid_generator.get_uuid(0x180A)
        self.config_uuid = None
        self.data_uuid = uuid_generator.get_uuid(0x2A24)
        self.period_uuid = None
        self.on = None  # does not need to be switched on!

        ble_utility.Service.__init__(self, periph, uuid_generator, self.service_uuid,
                                 self.config_uuid,
                                 self.data_uuid, "device")

    def read(self):
        # returns device name - the model number string
        val = self.data.read()
        return val