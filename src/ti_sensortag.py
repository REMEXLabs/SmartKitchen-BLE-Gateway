import ble_utility
import struct

'''
Basic BLE implementation for the TI Sensortag CC2650
'''

'''
Reading the battery status
'''


class Battery(ble_utility.Service):

    def __init__(self, periph):
        uuid_generator = ble_utility.UUID()

        self.service_uuid = uuid_generator.get_uuid(0x180F)
        self.config_uuid = None
        self.data_uuid = uuid_generator.get_uuid(0x2A19)
        self.period_uuid = None
        self.on = None  # does not need to be switched on!

        ble_utility.Service.__init__(self, periph, uuid_generator, self.service_uuid,
                                 self.config_uuid,
                                 self.data_uuid, "battery")

    def read(self):
        # returns the battery level in percent
        val = ord(self.data.read())
        return val

'''
Reading the ambient temperature of the TI Sensortag CC2650
'''


class Temp(ble_utility.Service):
    scaling = 0.03125

    def __init__(self, periph):
        uuid_generator = ble_utility.TI_UUID()

        self.service_uuid = uuid_generator.get_uuid(0xAA00)
        self.config_uuid = uuid_generator.get_uuid(0xAA02)
        self.data_uuid = uuid_generator.get_uuid(0xAA01)
        self.period_uuid = uuid_generator.get_uuid(0xAA03)

        ble_utility.Service.__init__(self, periph, uuid_generator,
                                     self.service_uuid, self.config_uuid,
                                     self.data_uuid, "temp")
        self.add_characteristics("period", self.period_uuid)

    def read(self):
        data = struct.unpack("<hh", self.data.read())
        ambt = (data[1] >> 2) * self.scaling
        return "%.1f" % ambt

    def set_probe_period(self, period):
        self.additional_characteristics["period"].write(period)

'''
Reading the humidity level
'''


class Humidity(ble_utility.Service):
    def __init__(self, periph):
        uuid_generator = ble_utility.TI_UUID()

        self.service_uuid = uuid_generator.get_uuid(0xAA20)
        self.conf_uuid = uuid_generator.get_uuid(0xAA22)
        self.data_uuid = uuid_generator.get_uuid(0xAA21)
        self.period_uuid = uuid_generator.get_uuid(0XAA23)

        ble_utility.Service.__init__(self, periph, uuid_generator,
                                     self.service_uuid, self.conf_uuid,
                                     self.data_uuid, "humidity")
        self.add_characteristics("period", self.period_uuid)

    def read(self):
        data = struct.unpack("<HH", self.data.read())
        humidity = 100.0 * (data[1] / 65536.0)
        return "%.1f" % humidity

    def set_probe_period(self, period):
        self.additional_characteristics["period"].write(period)

'''
Reading the barometer value 
'''


class Barometer(ble_utility.Service):
    def __init__(self, periph):
        uuid_generator = ble_utility.TI_UUID()

        self.service_uuid = uuid_generator.get_uuid(0xAA40)
        self.conf_uuid = uuid_generator.get_uuid(0xAA42)
        self.data_uuid = uuid_generator.get_uuid(0xAA41)
        self.period_uuid = uuid_generator.get_uuid(0xAA44)

        ble_utility.Service.__init__(self, periph, uuid_generator,
                                     self.service_uuid, self.conf_uuid,
                                     self.data_uuid, "barometer")
        self.add_characteristics("period", self.period_uuid)

    def read(self):
        data = struct.unpack("<BBBBBB", self.data.read())
        pressure = (data[3] + data[4] * 256 + data[5] * 65536) / 100
        return "%.0f" % pressure

    def set_probe_period(self, period):
        self.additional_characteristics["period"].write(period)

'''
Reading the lightning value
'''


class Lux(ble_utility.Service):
    def __init__(self, periph):
            uuid_generator = ble_utility.TI_UUID()

            self.service_uuid = uuid_generator.get_uuid(0xAA70)
            self.conf_uuid = uuid_generator.get_uuid(0xAA72)
            self.data_uuid = uuid_generator.get_uuid(0xAA71)
            self.period_uuid = uuid_generator.get_uuid(0xAA73)

            ble_utility.Service.__init__(self, periph, uuid_generator,
                                             self.service_uuid, self.conf_uuid,
                                             self.data_uuid, "lux")
            self.add_characteristics("period", self.period_uuid)

    def read(self):
        raw = struct.unpack('<h', self.data.read())[0]
        m = raw & 0xFFF
        e = (raw & 0xF000) >> 12
        return 0.01 * (m << e)

    def set_probe_period(self, period):
           self.additional_characteristics["period"].write(period)
