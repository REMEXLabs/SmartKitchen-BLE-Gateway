import threading
import time
import Queue
import logging

import src.ble_utility as BLEU
import src.rest_utility as REST
import src.ti_sensortag as TI
import src.utils as UTIL

class TIInterface(threading.Thread):
    prev_state = {}

    def __init__(self, address, queue, timeout, update, ble_dict):

        self.sensortag = BLEU.BLEDevice(address)
        self.sensortag.add_service("temperature", TI.Temp(self.sensortag))
        self.sensortag.add_service("humidity", TI.Humidity(self.sensortag))
        self.sensortag.add_service("barometer", TI.Barometer(self.sensortag))
        self.sensortag.add_service("lux", TI.Lux(self.sensortag))
        self.sensortag.add_service("battery", TI.Battery(self.sensortag))
        #for service in self.sensortag.services.itervalues():
        self.keys = self.sensortag.services.keys()
        print "keys : %s" % self.keys
        for key in self.keys:
            self.sensortag.services[key].activate()
        self.update_queue = queue
        self.ble_dict = ble_dict
        self.timeout = timeout
        self.update = update
        threading.Thread.__init__(self, target=self.get_current_values)

        # Give the Tag time to start data collection
        time.sleep(1.0)

        for key in self.keys:
           value = str(self.sensortag.services[key].read())
           print "On TTI nitialize. Service with value : %s %s" % (key, value)
           self.prev_state[key] = value
          # self.update_queue.put({key: value})
           ble_dict[key] = value

    def set_logger(self, logger_name):
        self.sensortag.set_logger(logger_name)

    def __del__(self):
        self.sensortag.disconnect()
        del (self.sensortag)

    def get_service_ids(self):
        return self.keys #Returning the keys
        service_ids = []
        for s_id in self.sensortag.services.iterkeys():
            service_ids.append(s_id)
        return service_ids

    def wait_for_notifications(self):
        self.sensortag.waitForNotifications(self.timeout)

    def get_current_values(self):
        self.update = True
        print "in get_current_values, before while true"
        while self.update:
            keys = self.sensortag.services.keys()
            print "in loop ... values are : %s" % self.keys
            for key in self.keys:
                cur_value = str(self.sensortag.services[key].read())
                print "Service with value : %s %s" % (key, cur_value)
                self.sensortag.logger.debug("Cur Value for %s: %s" % (key, cur_value))
                if self.prev_state[key] != cur_value:
                  #  self.update_queue.put({key: cur_value})
                    self.ble_dict[key] = cur_value
                self.prev_state[key] = cur_value
               # self.update_queue.put({key: cur_value})
                self.ble_dict[key] = cur_value

            self.wait_for_notifications()


class MainThread():

    prefix = "ble_imp_test"
    switch_queue = Queue.Queue(1)
    value_queue = Queue.Queue()
    ble_queue = Queue.Queue(3)
    update = True

    def __init__(self, instance_id):

        UTIL.Logger("TI_Gateway", "ti_gateway.log", logging.DEBUG,
                    logging.DEBUG)
        self.logger = logging.getLogger("TI_Gateway")

        self.sensortag = TIInterface("24:71:89:BC:1D:01", self.ble_queue, 1.0,
                                     self.update)
        self.sensortag.daemon = True
        self.sensortag.set_logger("TI_Gateway")
        self.sensortag.start()

    def run(self):
        while self.update:
            time.sleep(0.2)

            while True:
                try:
                    item = self.switch_queue.get(True, 0.5)
                    self.switch_queue.task_done()
                    key, value = item.popitem()
                    if value == "OFF":
                        self.update = False
                        break
                except:
                    break

            while True:
                try:
                    item = self.ble_queue.get(True, 0.5)
                    key, value = item.popitem()
                    self.rest_values.update_item_state("%s_%s" % (self.prefix,
                                                                  key),
                                                       str(value))
                    self.logger.debug("New State of %s: %s" %
                                      (str(key), str(value)))
                    self.ble_queue.task_done()
                except:
                    break

        # Clean Up
        self.logger.debug("Cleaning Up")

        # Set Values to NULL
        for service_id in self.sensortag.get_service_ids():
            self.rest_values.update_item_state("%s_%s" % (self.prefix,
                                                          service_id), "--")

        self.sensortag.__del__()  # Stop Sensortag


if __name__ == "__main__":
    main_thread = MainThread("ble_rest_test")
    main_thread.run()
