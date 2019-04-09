#!/usr/bin/python
import json
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

def format_popup(readings):
    ret = '<ul>\n'
    for key, value in readings.items():
        ret += f'<li>{key}: {value}</li>\n'
    ret += '</ul>'
    return ret

class myHandler(BaseHTTPRequestHandler):
    
    #Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        records = []
        for sensor_id, group in pandas.read_sql('select * from master order by created_at asc;', engine).drop_duplicates('sensor_id').groupby('machine_id'):
            record = json.loads(group.iloc[0].to_json())
            record['reading'] = format_popup(dict(zip(group.sensor_type, group.sensor_value)))
            record.pop('sensor_type')
            record.pop('sensor_value')
            records.append(record)
        with open(os.path.join(here, 'map.html'), 'r') as f:
            response = f.read()
        self.wfile.write(macro_expand(response, readings=json.dumps(records)).encode())
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
