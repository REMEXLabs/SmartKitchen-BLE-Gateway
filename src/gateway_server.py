#!/usr/bin/python
# -*- coding: utf-8 -*-
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from ti_gateway import TIInterface
import time
import Queue
import logging
import threading
from urlparse import urlparse, parse_qs
import urllib
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
        print "+++++++ Request empfangen QUTE" + " " + self.path + " -----> "

        print "+++++++ Request empfangen " + " " +  urllib.unquote(self.path) + " -----> "
       # parsed = urlparse.urlparse(self.path)
        # print urlparse.parse_qs(parsed.query)
        query_components = parse_qs(urlparse(urllib.unquote(self.path)).query)
        #parsed_query = urlparse.parse_qs(parsed.query)
        if  query_components: # check if param attribute is NOT empty
            print query_components
            whichData = query_components['sensorData'][0]
            print whichData
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
           # print "para '" + parsed_query + "' has the value: " + str(value)
            if(whichData == "all"):
                self.wfile.write("Temperatur ist: " + ble_dict["temperature"] + " Grad Celsius </p>")
                self.wfile.write("Luftfeuchtigkeit ist: " + ble_dict["humidity"] + "% </p>")
                self.wfile.write("Luftdruck ist: " + ble_dict["barometer"] + "Pa </p>")
        # Send the html message
            elif (whichData == "temprature"):
                self.wfile.write("Temperatur ist: " + ble_dict["temperature"] + " Grad Celsius </p>")
            elif (whichData == "humidity"):
                self.wfile.write("Luftfeuchtigkeit ist: " + ble_dict["humidity"] + "% </p>")
            elif (whichData == "barometer"):
                self.wfile.write("Luftdruck ist: " + ble_dict["barometer"] + "Pa </p>")
            elif (whichData == "temp"):
                self.wfile.write(ble_dict["temperature"])
            else:
                self.wfile.write("No valid parameter")

            self.wfile.close()
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

