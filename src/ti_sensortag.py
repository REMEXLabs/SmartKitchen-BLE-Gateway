import ble_utility

import struct


class Temp(ble_utility.Service):
    scaling = 0.03125

    def __init__(self, periph):
        uuid_generator = ble_utility.UUID("%08X-0451-4000-b000-000000000000",
                                          0xF0000000)
        self.service_uuid = 0xAA00
        self.config_uuid = 0xAA02
        self.data_uuid = 0xAA01
        self.period_uuid = 0xAA03
        ble_utility.Service.__init__(self, periph, uuid_generator,
                                     self.service_uuid, self.config_uuid,
                                     self.data_uuid, "temp")
        self.add_characteristics("period", self.period_uuid)

    def read(self):
        data = struct.unpack("<hh", self.data.read())
        t = (data[0] >> 2) * self.scaling
        ambt = (data[1] >> 2) * self.scaling
        return (t, ambt)

    def set_probe_period(self, period):
        self.additional_characteristics["period"].write(period)


class Humidity(ble_utility.Service):
    def __init__(self, periph):
        uuid_generator = ble_utility.UUID("%08X-0451-4000-b000-000000000000",
                                          0xF0000000)
        self.service_uuid = 0xAA20
        self.conf_uuid = 0xAA22
        self.data_uuid = 0xAA21
        self.period_uuid = 0XAA23
        ble_utility.Service.__init__(self, periph, uuid_generator,
                                     self.service_uuid, self.conf_uuid,
                                     self.data_uuid, "humidity")
        self.add_characteristics("period", self.period_uuid)

    def read(self):
        data = struct.unpack("<HH", self.data.read())
        temp = -40.0 + 165.0 * (data[0] / 65536.0)
        humidity = 100.0 * (data[1] / 65536.0)
        return (temp, humidity)

    def set_probe_period(self, period):
        self.additional_characteristics["period"].write(period)


class Barometer(ble_utility.Service):
    def __init__(self, periph):
        uuid_generator = ble_utility.UUID("%08X-0451-4000-b000-000000000000",
                                          0xF0000000)
        self.service_uuid = 0xAA40
        self.conf_uuid = 0xAA42
        self.data_uuid = 0xAA41
        self.period_uuid = 0xAA44

        ble_utility.Service.__init__(self, periph, uuid_generator,
                                     self.service_uuid, self.conf_uuid,
                                     self.data_uuid, "barometer")
        self.add_characteristics("period", self.period_uuid)

    def read(self):
        data = struct.unpack("<BBBBBB", self.data.read())
        temp = (data[0] + data[1] * 256 + data[2] * 65536) / 100
        pressure = (data[3] + data[4] * 256 + data[5] * 65536) / 100
        return (temp, pressure)

    def set_probe_period(self, period):
        self.additional_characteristics["period"].write(period)
