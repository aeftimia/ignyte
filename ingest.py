import json
import os
import pandas
import sqlalchemy
import urllib.parse

username = os.environ['ignyte_db_username']
password = urllib.parse.quote(os.environ['ignyte_db_password'])
db = urllib.parse.quote(os.environ['ignyte_db'])
engine = sqlalchemy.create_engine(f'postgresql+psycopg2://{username}:{password}@localhost/{db}')

here = os.path.dirname(os.path.realpath(__file__))
for dirpath, dirnames, filenames in os.walk(os.path.join(here, 'data')):
    for filename in filenames:
        if filename[-4:] != '.csv':
            continue
        df = pandas.read_csv(os.path.join(dirpath, filename))
        df.columns = [column.lower().replace(' ', '_') for column in df.columns]
        tablename = filename.lower()[:-4].replace(' ', '_')
        engine.execute('drop table if exists {0} cascade;'.format(tablename))
        df.to_sql(tablename, engine, index=False)


with open(os.path.join(here, 'schema.json')) as f:
    schema = json.load(f)

for tablename, constraints in schema.items():
    primary_key = constraints['primary_key']
    sql = f'ALTER TABLE {tablename} ADD PRIMARY KEY ({primary_key});'
    engine.execute(sql)

for tablename, constraints in schema.items():
    if not 'foreign_key' in constraints:
        continue

    for i, (foreign_key, foreign_tablename, primary_key) in enumerate(constraints['foreign_key']):
        sql = f'ALTER TABLE {tablename} ADD CONSTRAINT foreign_reference_{i} FOREIGN KEY ({foreign_key}) REFERENCES {foreign_tablename} ({primary_key});'.format(i)
        engine.execute(sql)

engine.execute('ALTER TABLE sensor_readings ADD COLUMN created_at TIMESTAMP DEFAULT NOW()')

with open(os.path.join(here, 'sql', 'proceedure.sql')) as f:
    engine.execute(f.read())
