#!/usr/bin/python
import os
import pandas
import sqlalchemy

from http.server import BaseHTTPRequestHandler,HTTPServer
from utils import macro_expand

engine = sqlalchemy.create_engine('postgresql+psycopg2://aeftimia@localhost/ignyte')
here = os.path.dirname(os.path.realpath(__file__))
PORT_NUMBER = 8080

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
    
    #Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        with open(os.path.join(here, 'map.html'), 'r') as f:
            response = f.read()
        self.wfile.write(response.encode())
        return

try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)

    #Wait forever for incoming htto requests
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
