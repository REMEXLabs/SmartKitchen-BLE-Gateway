import ti_sensortag
import ble_utility

import struct
import time


def main():
    print("Connecting to Tag 24:71:89:BC:1D:01")
    tag = ble_utility.BLEDevice("24:71:89:BC:1D:01")
    tag.add_service("temp", ti_sensortag.Temp(tag))
    tag.services["temp"].activate()
    period = struct.pack("B", 0x1E)  # This sets the Sensor to 300ms
    tag.services["temp"].set_probe_period(period)

    time.sleep(1.0)

    i = 1
    while True:
        print("TempSensor: ", tag.services["temp"].read())
        if i > 4:
            break
        i += 1
        tag.waitForNotifications(1.0)

    tag.disconnect()
    del tag


if __name__ == '__main__':
    main()
