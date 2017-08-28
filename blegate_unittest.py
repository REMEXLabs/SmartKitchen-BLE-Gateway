import Queue
import struct
import time
import unittest

import peripherals.TI.sensortag as TI
import src.ble_utility as BLEU
import src.rest_utility as REST


class BLETest(unittest.TestCase):
    def test_ti(self):
        tag = BLEU.BLEDevice("24:71:89:BC:1D:01")
        tag.add_service("temp", TI.Temp(tag))
        tag.services["temp"].activate()
        period = struct.pack("B", 0x1E)  # This sets the Sensor to 300ms
        tag.services["temp"].set_probe_period(period)

        time.sleep(1.0)

        for i in range(0, 4):
            self.assertTrue(tag.services["temp"].read() is not None)
            tag.waitForNotifications(1.0)

        tag.disconnect()
        del tag


class RESTTest(unittest.TestCase):
    update_queue = Queue.Queue(1)
    # Use default values for openHabianpi, change values if necessary
    rest_interface = REST.OpenHabRestInterface("192.168.178.20", "8080", "pi",
                                               "raspberry", "rest_group",
                                               update_queue)
    rest_interface.daemon = True  # Daemonize the Thread

    def test_update_get(self):
        # Update and Get Item Test
        for i in range(1, 20):
            self.assertTrue(
                self.rest_interface.update_item_state("rest_test", i))
            self.assertEqual(
                self.rest_interface.get_item_state("rest_test"), str(i))

    def test_polling(self):
        # Prevent updates so poll_status gets a queue
        self.assertTrue(
            self.rest_interface.update_item_state("rest_test", "0", True))
        self.rest_interface.start()
        for i in range(1, 20):
            items = self.update_queue.get()
            self.assertTrue(("rest_test") in items.keys())
            self.assertEqual(items["rest_test"], str(i - 1))
            self.assertTrue(
                self.rest_interface.update_item_state("rest_test", i))
            self.update_queue.task_done()
        self.rest_interface.update = False

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

    def test_item_delete(self):
        self.assertTrue(
            self.rest_interface.add_item("unittest_rest", "String", "", "rest",
                                         "rest_group"))
        self.assertTrue(self.rest_interface.delete_item("unittest_rest"))
        self.assertFalse(self.rest_interface.get_item_state("unittest_rest"))


if __name__ == '__main__':
    unittest.main()
