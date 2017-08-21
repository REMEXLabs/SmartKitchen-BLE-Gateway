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
            BLEDevice("BLE_Thread")
            server.serve_forever()

        except KeyboardInterrupt:
            print '^C received, shutting down the web server'
            server.socket.close()


# This class will handles any incoming request from
# the browser
class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        print "+++++++ incoming request --->  " + self.path
        unquoted_query_components = parse_qs(urlparse(urllib.unquote(self.path)).query)
        if unquoted_query_components:
            if unquoted_query_components['data']:
                self.handel_get_data_request(unquoted_query_components)
            elif unquoted_query_components['action']:
                self.handel_action_request(unquoted_query_components)
        return

    def handel_get_data_request(self, unquoted_query_components):
        _sensor_data_query = unquoted_query_components['data'][0]
        print _sensor_data_query
        if _sensor_data_query == "all":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            # TODO: Refactor this part with proper JSON lib.
            self.wfile.write("{" +
                             "\"sensorData\": {" +
                             "\"temperature\":" + "\"" + ble_dict["temperature"] + "\"," +
                             "\"humidity\":" + "\"" + ble_dict["humidity"] + "\"," +
                             "\"pressure\":" + "\"" + ble_dict["barometer"] + "\"," +
                             "\"lux\":" + "\"" + ble_dict["lux"] + "\"," +
                             "\"battery\":" + "\"" + ble_dict["battery"] + "\"" +
                             "}"
                             '}')
            self.wfile.close()
        else:
            self.send_response(200)
            self.send_header('Content-type', 'plain/text')
            self.end_headers()
            self.wfile.write("no valid parameter")
            self.wfile.close()
        return

    def handel_action_request(self, action):
        return


class BLEDevice:

    prefix = "BLE Device"
    update = True

    def __init__(self):
        UTIL.Logger("TI_Gateway", "ti_gateway.log", logging.DEBUG, logging.DEBUG)
        self.logger = logging.getLogger("TI_Gateway")
        self.ble_device = TIInterface("24:71:89:BC:1D:01", ble_queue, 1.0, self.update, ble_dict)
        self.ble_device.daemon = True
        self.ble_device.set_logger("TI_Gateway")
        self.ble_device.start()


class main:
    def __init__(self):
        server = http_server(8080, RequestHandler)
        server.run()

if __name__ == '__main__':
    m = main()

