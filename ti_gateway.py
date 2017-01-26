import threading
import time

import src.ble_utility as BLEU
import src.rest_utility as REST
import src.ti_sensortag as TI


class TIInterface(threading.Thread):
    prev_state = {}
    update = False

    def __init__(self, address, queue, timeout):
        self.sensortag = BLEU.BLEDevice(address)
        self.sensortag.add_service("temperature", TI.Temp(self.sensortag))
        self.sensortag.add_service("humidity", TI.Humidity(self.sensortag))
        self.sensortag.add_service("barometer", TI.Barometer(self.sensortag))
        for service in self.sensortag.services.itervalues():
            service.activate()
        self.update_queue = queue
        self.queue_lock = threading.BoundedSemaphore()
        self.timeout = timeout

        # Give the Tag time to start data collection
        time.sleep(1.0)

        for s_id, service in self.sensortag.services.iteritems():
            value = service.read()
            self.prev_state[s_id] = value
            with self.queue_lock:  # Write to queue for initialization
                self.update_queue[s_id] = value

    def __del__(self):
        self.sensortag.disconnect()
        del(self.sensortag)

    def get_service_ids(self):
        service_ids = []
        for s_id in self.sensortag.services.iterkeys():
            service_ids.append(s_id)
        return service_ids

    def wait_for_notifications(self):
        self.sensortag.waitForNotifications(self.timeout)

    def run(self):
        self.update = True

        while self.update:
            for s_id, service in self.sensortag.services.iteritems():
                curr_value = service.read()
                if self.prev_state[s_id] != curr_value:
                    with self.queue_lock:
                        self.update_queue[s_id] = curr_value

            self.wait_for_notifications()

    def stop_update(self):
        self.update = False


class MainThread():
    prefix = "ble_imp_test"
    switch_queue = {}
    value_queue = {}
    ble_queue = {}
    queue_lock = threading.BoundedSemaphore()

    def __init__(self, instance_id):
        self.rest_switches = REST.OpenHabRestInterface(
            "192.168.178.24", "8080", "pi", "raspberry", self.switch_queue)
        self.rest_values = REST.OpenHabRestInterface("192.168.178.24", "8080",
                                                     "pi", "raspberry", self.value_queue)
        self.sensortag = TIInterface("24:71:89:BC:1D:01",
                                     self.ble_queue, 1.0)

        # Create Switch items
        self.rest_switches.add_item("%s_device_switch_group" % self.prefix, "group",
                                    "Group of Switches for %s" % self.prefix, "rest", "")
        self.rest_switches.add_item("%s_device_switch" % self.prefix, "Switch",
                                    "Switch for %s" % self.prefix, "rest", "%s_device_switch_group" % self.prefix)
        self.rest_switches.update_item_state(
            "%s_device_switch" % self.prefix, "ON")
        self.rest_switches.set_group("%s_device_switch_group" % self.prefix)

        self.rest_switches.start()

        # Create Value items
        self.rest_values.add_item("%s_values_group" % self.prefix, "Group",
                                  "Group of Values for %s" % self.prefix, "rest", "")
        for service_id in self.sensortag.get_service_ids():
            self.rest_values.add_item("%s_%s" % (
                self.prefix, service_id), "String", service_id, "rest", "%s_values" % self.prefix)

    def run(self):
        # Start
        self.sensortag.start()

        while True:
            update_items = {}
            switch_value = None

            with self.queue_lock:
                for item, value in self.switch_queue:
                    if item == "%s_device_switch" % self.prefix:
                        switch_value = value
                    self.switch_queue = {}

            if switch_value == "OFF":
                break

            with self.queue_lock:
                for item, value in self.ble_queue.iteritems():
                    update_items[item] = value
                self.ble_queue = {}

            for item, value in update_items:
                self.rest_values.update_item_state(item, state)

        # Clean Up
        # Stop BLE
        self.sensortag.stop_update()
        self.sensortag.__del__()
        self.sensortag.join()

        # Set Values to NULL
        for service_id in self.sensortag.get_service_ids:
            self.rest_values.update_item_state(service_id, "NULL")
        self.rest_values.join()

        # Stop switch updates
        self.rest_switches.stop_update()
        self.rest_switches.join()


if __name__ == "__main__":
    main_thread = MainThread("ble_rest_test")
    main_thread.run()
