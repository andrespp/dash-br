"""app.py
"""
import dash
import dash_auth
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import configparser
import locale
import os
import uetl
import dwbr

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

## FULL DW from parquet files
try:
    DWC = dwbr.load_dw(config['FULLDW']['DATADIR'])
except Exception as e:
    DWC = None
    print(f'WARN: Unable to open parquet files. {e}')

## Dash app object (flask application)
THEME = dbc.themes.BOOTSTRAP
#ICONS = dbc.icons.BOOTSTRAP
ICONS = dbc.icons.FONT_AWESOME
app = dash.Dash(__name__,
                external_stylesheets=[THEME, ICONS],
                 meta_tags=[{'name': 'viewport',
                             'content': 'width=device-width, \
                                         initial-scale=0.8,  \
                                         maximum-scale=1.0,  \
                                         minimum-scale=0.5,'
                            }]
               )
app.config.suppress_callback_exceptions=True

# Basic Authentication
if config['SITE']['AUTH']=='True':
    auth = dash_auth.BasicAuth(app, config._sections['USERS'])

# Enable logging
if config['SITE']['LOG']=='True':
    VERBOSE=True
else:
    VERBOSE=False

# Placeholder for futures translation
def _(foo: str):
    return foo


print(f"Dash v{dash.__version__}.\n" \
      f"DCC v{dcc.__version__}.\n" \
      f"DBC v{dbc.__version__}")

if DWC:
    print(f'dash-sql tables are:\n {DWC.sql("SHOW TABLES").compute()}')
