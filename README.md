# Setup

## Dependencies
Make sure you have a postgres client, python3, and git lfs. git lfs pull the data files.

When cloning, use `git clone --recurse-submodules`.

## Database
Make sure to have a recent installation of postgres running. Pick a postgres username, password, and database for working with sensor data, and create the associated username database on the postgres server. Make sure the chosen user has the ability to read, write, create, and drop new tables and functions.

## Environment Variables
Export the chosen username, password, and database as the following environment variables:
```
export ignyte_db_username=<username>
export ignyte_db_password=<password>
export ignyte_db_=<database name>
```

## Python

```
virtualenv --python=python3 venv
source venv/bin/activate
pip install -r requirements.txt
```

## Load and Collect Data
`git lfs pull`
`python ingest.py && bash background.sh > /dev/null &`

# Start Server
`python dashboard/server.py`

You may now open your browser to `localhost:5000` to see the interface.
