#!/usr/bin/python
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
PORT_NUMBER= 8080

class http_server:
    def __init__(self):

        try:
            # Create a web server and define the handler to manage the
            # incoming request
            server = HTTPServer(('', PORT_NUMBER), requestHandler)
            print 'Started httpserver on port ', PORT_NUMBER

            # Wait forever for incoming htto requests
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
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
        # Send the html message
        # self.wfile.write("Hello, deine Anfrage war:" + parsed_query['yolo'])
        return

class main:
    def __init__(self):
        self.server = http_server()

if __name__ == '__main__':
    m = main()

