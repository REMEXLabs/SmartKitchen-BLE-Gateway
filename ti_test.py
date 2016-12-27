import src.ti_sensortag as TI
import src.ble_utility as BLEU

import struct
import time
import logging


def main():
    tag = BLEU.BLEDevice("24:71:89:BC:1D:01", True, logging.DEBUG)
    tag.add_service("temp", TI.Temp(tag))
    tag.services["temp"].activate()
    period = struct.pack("B", 0x1E)  # This sets the Sensor to 300ms
    tag.services["temp"].set_probe_period(period)

    time.sleep(1.0)

    i = 1
    while True:
        tag.services["temp"].log_value(tag.logger)
        if i > 4:
            break
        i += 1
        tag.waitForNotifications(1.0)

    tag.disconnect()
    del tag


if __name__ == '__main__':
    main()
