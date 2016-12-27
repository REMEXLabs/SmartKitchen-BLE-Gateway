import ble_utility

import struct


class Temp(ble_utility.Service):
    scaling = 0.03125

    def __init__(self, periph):
        uuid = ble_utility.UUID("%08X-0451-4000-b000-000000000000", 0xF0000000)
        self.service_uuid = uuid.get_uuid(0xAA00)
        self.config_uuid = uuid.get_uuid(0xAA02)
        self.data_uuid = uuid.get_uuid(0xAA01)
        self.period_uuid = uuid.get_uuid(0xAA03)
        ble_utility.Service.__init__(self, periph, self.service_uuid,
                                     self.config_uuid, self.data_uuid, "temp")
        self.add_characteristics("period", self.period_uuid)

    def read(self):
        data = struct.unpack("<hh", self.data.read())
        t = (data[0] >> 2) * self.scaling
        ambt = (data[1] >> 2) * self.scaling
        return (t, ambt)

    def set_probe_period(self, period):
        self.additional_characteristics["period"].write(period)
