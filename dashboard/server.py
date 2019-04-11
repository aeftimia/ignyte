#!/usr/bin/python
import json
import os
import pandas
import sqlalchemy
import urllib.parse

import flask
import random

from flask import Flask, redirect, url_for, request, render_template, send_from_directory

engine = sqlalchemy.create_engine('postgresql+psycopg2://aeftimia@localhost/ignyte')
here = os.path.dirname(os.path.realpath(__file__))
PORT_NUMBER = 8080

app = Flask(__name__,  static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or \
    'e5ac358c-f0bf-11e5-9e39-d3b532c10a28'

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

@app.route('/')
def index():
    if 'executive' in request.args:
        return redirect(url_for('executive'))
    return redirect(url_for('operations'))

@app.route('/executive')
def executive():
    records = []
    data = pandas.read_sql('select * from master order by created_at, location desc;', engine)
    data['abnormal'] = data.sensor_value.map(is_abmormal)
    x = ['x',] + data.created_at.apply(lambda x: x.strftime('%B %d, %Y, %r')).values.tolist()
    columns = [x]
    for location, group in data.groupby('location'):
        column = [location,] + group.groupby('created_at').abnormal.agg('mean').values.tolist()
        columns.append(column)
    return render_template('chart.html')

@app.route('/operations')
def operations():
    records = []
    for location, group in pandas.read_sql('select * from master order by created_at desc;', engine).drop_duplicates('sensor_id').groupby('location'):
        record = json.loads(group.iloc[0].to_json())
        record['reading'], record['abnormal'] = format_popup(group.groupby('machine_id'))
        record['reading'] = f'{location}<br>\n' + record['reading']
        record.pop('sensor_type')
        record.pop('sensor_value')
        records.append(record)
    return render_template('map.html', readings=json.dumps(records))

@app.route('/c3/<path:path>')
def send_c3(path):
    return send_from_directory('c3', path)

if __name__ == '__main__':
    app.run()
