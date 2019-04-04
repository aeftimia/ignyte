import os
import pandas
import sqlalchemy

engine = sqlalchemy.create_engine('postgresql+psycopg2://aeftimia@localhost/ignyte')

here = os.path.dirname(os.path.realpath(__file__))
for dirpath, dirnames, filenames in os.walk(os.path.join(here, 'data')):
    for filename in filenames:
        df = pandas.read_csv(os.path.join(dirpath, filename))
        tablename = filename.lower()[:-4].replace(' ', '_')
        engine.execute('drop table if exists {0};'.format(tablename))
        df.to_sql(tablename, engine)
