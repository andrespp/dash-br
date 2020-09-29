"""app.py
"""
import dash
import dash_auth
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import configparser
import locale
import os.path
import uetl

## Settings
CONFIG_FILE = 'config.ini'

# Read configuration File
if not os.path.isfile(CONFIG_FILE):
    print('ERROR: file "{}" does not exist'.format(CONFIG_FILE))
    exit(-1)
try:
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
except:
    print('ERROR: Unable to read config file ("{}")'.format(CONFIG_FILE))
    exit(-1)

# Set locale
locale.setlocale(locale.LC_MONETARY, config['SITE']['LANG'])

## DWO Object
# Initialize Data Warehouse object
DWO = uetl.DataWarehouse(name=config['DW']['NAME'],
                         dbms=config['DW']['DBMS'],
                         host=config['DW']['HOST'],
                         port=config['DW']['PORT'],
                         base=config['DW']['BASE'],
                         user=config['DW']['USER'],
                         pswd=config['DW']['PASS'])
# Test dw db connection
if DWO.test_conn():
    print('Data Warehouse DB connection succeed!')
else:
    print('ERROR: Data Warehouse DB connection failed!')
    exit(-1)

## Dash app object (flask application)
THEME = dbc.themes.BOOTSTRAP
app = dash.Dash(__name__, external_stylesheets=[THEME])
app.config.suppress_callback_exceptions=True

# Basic Authentication
if config['SITE']['AUTH']=='True':
    auth = dash_auth.BasicAuth(app, config._sections['USERS'])

# Enable logging
if config['SITE']['LOG']=='True':
    VERBOSE=True
else:
    VERBOSE=False

print(f"Dash version is {dcc.__version__}")
