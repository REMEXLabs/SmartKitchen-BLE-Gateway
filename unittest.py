import logging
import struct
import time
import unittest

import src.ble_utility as BLEU
import src.ti_sensortag as TI
import src.rest_utility as REST


class BLETest(unittest.TestCase):
    def ti_test(self):
        tag = BLEU.BLEDevice("24:71:89:BC:1D:01")
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


class RESTTest(unittest.TestCase):
    update_queue = {}
    # Use default values for openHabianpi, change values if necessary
    rest_interface = REST.OpenHabRestInterface("192.168.178.24", "8080", "pi",
                                               "raspberry", update_queue)
    rest_interface.start()

    def test_update_get(self):
        # Update and Get Item Test
        for i in range(1, 20):
            self.assertTrue(
                self.rest_interface.update_item_state("rest_test", i))
            self.assertEqual(
                self.rest_interface.get_item_state("rest_test"), str(i))

    def test_polling(self):
        # Prevent updates dor the next one to get a queue
        self.assertTrue(
            self.rest_interface.update_item_state("rest_test", "0", True))
        for i in range(1, 20):
            self.assertTrue(self.rest_interface.poll_status("rest_group"))
            items = self.rest_interface.get_queue()
            self.assertEqual(len(items), 1)
            self.assertTrue(("rest_test") in items.keys())
            self.assertEqual(items["rest_test"], str(i - 1))
            self.assertTrue(
                self.rest_interface.update_item_state("rest_test", i))

    def test_item_create(self):
        self.assertTrue(
            self.rest_interface.add_item("unittest_rest", "String",
                                         "Item created by unittest", "rest",
                                         "rest_group"))
        self.assertTrue(
            self.rest_interface.update_item_state("unittest_rest",
                                                  "test_1337_test"))
        self.assertEqual(
            self.rest_interface.get_item_state("unittest_rest"),
            "test_1337_test")

    rest_interface.join()


if __name__ == '__main__':
    unittest.main()
    del (unittest_logger)
