import threading
import time

import peripherals.EGO.cooktop as ego
import src.ble_utility as BLEU


class EGOInterface(threading.Thread):
    prev_state = {}

    def __init__(self, address, queue, timeout, update, ble_dict):

        self.cooktop = BLEU.BLEDevice(address)
        self.cooktop.add_service("vendor", ego.Vendor(self.cooktop))
        self.cooktop.add_service("device", ego.Device(self.cooktop))
        self.cooktop.add_service("status", ego.Status(self.cooktop))
        # self.sensortag.add_service("io", TI.IOService(self.sensortag))
        #for service in self.sensortag.services.itervalues():
        self.keys = self.cooktop.services.keys()
        print "keys : %s" % self.keys
        for key in self.keys:
            self.cooktop.services[key].activate()
        self.update_queue = queue
        self.ble_dict = ble_dict
        self.timeout = timeout
        self.update = update
        threading.Thread.__init__(self, target=self.get_current_values)

        # Give the Tag time to start data collection
        time.sleep(1.0)

        for key in self.keys:
            value = str(self.cooktop.services[key].read())
            print "On TTI initialize. Service with value : %s %s" % (key, value)
            self.prev_state[key] = value
            ble_dict[key] = value
            # self.update_queue.put({key: value})


    def set_logger(self, logger_name):
        self.cooktop.set_logger(logger_name)

    def __del__(self):
        self.cooktop.disconnect()
        del (self.cooktop)

    '''
    def get_service_ids(self):
        return self.keys #Returning the keys
        service_ids = []
        for s_id in self.sensortag.services.iterkeys():
            service_ids.append(s_id)
        return service_ids
    '''

    def wait_for_notifications(self):
        self.cooktop.waitForNotifications(self.timeout)

    def get_current_values(self):
        while self.update:
            for key in self.keys:
                cur_value = str(self.cooktop.services[key].read())
                print "Service with value : %s %s" % (key, cur_value)
                self.cooktop.logger.debug("Cur Value for %s: %s" % (key, cur_value))
                if self.prev_state[key] != cur_value:
                  #  self.update_queue.put({key: cur_value})
                    self.ble_dict[key] = cur_value
                self.prev_state[key] = cur_value
               # self.update_queue.put({key: cur_value})
                self.ble_dict[key] = cur_value

            self.wait_for_notifications()
