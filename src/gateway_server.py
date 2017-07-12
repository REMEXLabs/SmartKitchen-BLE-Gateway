#!/usr/bin/python
# -*- coding: utf-8 -*-
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from ti_gateway import TIInterface
import time
import Queue
import logging
import threading
import src.ble_utility as BLEU
import src.rest_utility as REST
import src.ti_sensortag as TI
import src.utils as UTIL

# The servers' port number.

switch_queue = Queue.Queue(1)
value_queue = Queue.Queue()
ble_queue = Queue.Queue(3)

ble_dict = {}

class http_server:

    def __init__(self, PORT_NUMBER,R_Handler):
        # The servers' port number.
        self.PORT_NUMBER = PORT_NUMBER
        self.Request_Handler = R_Handler

    def run(self):
        try:
            # Create a web server and define the handler to manage the
            # incoming request
            server = HTTPServer(('', self.PORT_NUMBER), self.Request_Handler)
            print 'Started httpserver on port ', self.PORT_NUMBER

            # Wait forever for incoming htto requests
            BLE_Thread("BLE_Thread")
            server.serve_forever()

        except KeyboardInterrupt:
            print '^C received, shutting down the web server'
            server.socket.close()


# This class will handles any incoming request from
# the browser
class requestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # f = furl(self.path)
        # print f.args['yolo']
        parsed = urlparse.urlparse(self.path)
        # print parsed.query
        # print urlparse.parse_qs(parsed.query)
        parsed_query = urlparse.parse_qs(parsed.query)

        if  parsed_query: # check if param attribute is NOT empty
            for para in parsed_query:
                value = parsed_query[para]
                print "para '" + para + "' has the value: " + str(value)
                print ble_dict["temperature"]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
        # Send the html message
            self.wfile.write("Hello: </p>")
            self.wfile.write("Temperatur ist: " + ble_dict["temperature"] + " Grad Celsius </p>")
            self.wfile.write("Luftfeuchtigkeit ist: " + ble_dict["humidity"] + "% </p>")
            self.wfile.write("Luftdruck ist: "  + ble_dict["barometer"] + "Pa </p>")
        return


class BLE_Thread():

    prefix = "ble_imp_test"

    update = True

    def __init__(self, instance_id):

        UTIL.Logger("TI_Gateway", "ti_gateway.log", logging.DEBUG,
                    logging.DEBUG)
        self.logger = logging.getLogger("TI_Gateway")

        self.sensortag = TIInterface("24:71:89:BC:1D:01", ble_queue, 1.0,
                                     self.update, ble_dict)
        self.sensortag.daemon = True
        self.sensortag.set_logger("TI_Gateway")
        self.sensortag.start()

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        while self.update:
            time.sleep(0.2)

            while True:
                try:
                    item = switch_queue.get(True, 0.5)
                    switch_queue.task_done()
                    key, value = item.popitem()
                    if value == "OFF":
                        self.update = False
                        break
                except:
                    break

            while True:
                try:
                    item = ble_queue.get(True, 0.5)
                    key, value = item.popitem()
                    self.rest_values.update_item_state("%s_%s" % (self.prefix,
                                                                  key),
                                                       str(value))
                    self.logger.debug("New State of %s: %s" %
                                      (str(key), str(value)))
                    ble_queue.task_done()
                except:
                    break

        # Clean Up
        self.logger.debug("Cleaning Up")

        # Set Values to NULL
        for service_id in self.sensortag.get_service_ids():
            self.rest_values.update_item_state("%s_%s" % (self.prefix,
                                                          service_id), "--")

        self.sensortag.__del__()  # Stop Sensortag

class main:
    def __init__(self):
        server = http_server(8080, requestHandler)
        server.run()

if __name__ == '__main__':
    m = main()
