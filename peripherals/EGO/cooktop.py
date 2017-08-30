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


class Status(ble_utility.Service):

    def __init__(self, periph):
        uuid_generator = ble_utility.UUID()

        self.service_uuid = uuid_generator.get_uuid("85205100-26dd-913f-4b8f-ee97799e304f")
        self.config_uuid = uuid_generator.get_uuid("85205101-26dd-913f-4b8f-ee97799e304f")
        self.data_uuid = uuid_generator.get_uuid("85205102-26dd-913f-4b8f-ee97799e304f")
        self.period_uuid = None
        self.on = None  # does not need to be switched on!

        ble_utility.Service.__init__(self, periph, uuid_generator, self.service_uuid,
                                 self.config_uuid,
                                 self.data_uuid, "status")

    def read(self):
        # returns device name - the model number string
        val = struct.unpack("cccc", self.data.read())

        print  val
        print  ('{0:08b}'.format(ord(val[0]))[::-1]) + ('{0:08b}'.format(ord(val[1]))[::-1])
        return val