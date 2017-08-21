import threading
import time
import src.ble_utility as BLEU
import src.ti_sensortag as TI


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
           print "On TTI initialize. Service with value : %s %s" % (key, value)
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
        while self.update:
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
