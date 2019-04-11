#!/usr/bin/python
import json
import os
import pandas
import sqlalchemy
import urllib.parse

from http.server import BaseHTTPRequestHandler,HTTPServer
from utils import macro_expand

engine = sqlalchemy.create_engine('postgresql+psycopg2://aeftimia@localhost/ignyte')
here = os.path.dirname(os.path.realpath(__file__))
PORT_NUMBER = 8080

#This class will handles any incoming request from
#the browser 

def is_abmormal(value):
    return value > 0.5

def format_popup(machines):
    ret = '<ul>\n'
    any_abnormal = False
    for machine, readings in machines:
        abnormal = False
        machine_type = readings.machine_type.iloc[0]
        machine = f'{machine_type}: {machine}'
        data = ''
        for key, value in zip(readings.sensor_type, readings.sensor_value):
            item = f'{key}: {value:.2f}'
            if is_abmormal(value):
                abnormal = True
                any_abnormal = True
                item = f'<font color="red">{item}</font>'
            data += f'<li>{item}</li>'
        if abnormal:
            machine = f'<font color="red">{machine}</font>'
        ret += f'<li>{machine}<ul>{data}</ul></li>\n'
    ret += '</ul>'
    return ret, any_abnormal

class myHandler(BaseHTTPRequestHandler):
    
    #Handler for the GET requests
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        # Send the html message
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        if not query:
            return self.send_map()
        return self.send_chart()

    def send_chart(self):
        records = []
        data = pandas.read_sql('select * from master order by created_at, location desc;', engine)
        data['abnormal'] = data.sensor_value.map(is_abmormal)
        x = ['x',] + data.created_at.apply(lambda x: x.strftime('%B %d, %Y, %r')).values.tolist()
        print(x)
        columns = [x]
        for location, group in data.groupby('location'):
            column = [location,] + group.groupby('created_at').abnormal.agg('mean').values.tolist()
            columns.append(column)
        with open(os.path.join(here, 'chart.html'), 'r') as f:
            response = f.read()
        self.wfile.write(response.encode())#, columns=json.dumps(columns)).encode())


    def send_map(self):
        records = []
        for location, group in pandas.read_sql('select * from master order by created_at desc;', engine).drop_duplicates('sensor_id').groupby('location'):
            record = json.loads(group.iloc[0].to_json())
            record['reading'], record['abnormal'] = format_popup(group.groupby('machine_id'))
            record['reading'] = f'{location}<br>\n' + record['reading']
            record.pop('sensor_type')
            record.pop('sensor_value')
            records.append(record)
        with open(os.path.join(here, 'map.html'), 'r') as f:
            response = f.read()
        self.wfile.write(macro_expand(response, readings=json.dumps(records)).encode())

try:
    #Create a web server and define the handler to manage the
    #incoming request
    server = HTTPServer(('', PORT_NUMBER), myHandler)

    #Wait forever for incoming htto requests
    server.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
    server.socket.close()
