import dash_bootstrap_components as dbc
import dash_daq as daq
import xlsxwriter
import urllib
import base64
import io
import pandas as pd
import traceback
from app import app
from dash.dependencies import Input, Output, State
from dash import dash_table
from dash import dcc, html
from uetl import DataWarehouse
from dask_sql import Context

###############################################################################
# Data lookup functions
###############################################################################
def lookup_data(dw, table=None, query=None, limit=None):
    """
    Lookup data from table. If query is provided, table is ignored and query is
    returned instead
    """
    if isinstance(dw, DataWarehouse):
        print('UETL DW!')
        return lookup_data_uetl(
            dw, table=table, query=query, limit=limit,
        )
    elif isinstance(dw, Context):
        print('DASK-SQL DW!')
        return lookup_data_dasksql(
            dw, table=table, query=query, limit=limit,
        )
    else:
        print('Invalid DW!')
        return None, None

def lookup_data_uetl(dw, table=None, query=None, limit=None):

    try:
        # Lookup data
        if query:
            df = dw.query(query)

        else:
            if limit:
                df = dw.query(f"SELECT * FROM {table} LIMIT {limit}")
            else:
                df = dw.query(f"SELECT * FROM {table}")

        df_len = len(df)


        return (df, df_len)

    except Exception as e:

        traceback.print_exc()

        a = pd.DataFrame([f'unnable to query table {table}.'],
                         columns=['error'],
                        )
        return (a, len(a))

def lookup_data_dasksql(dw, table=None, query=None, limit=None):

    try:
        # Lookup data
        if query:
            df = dw.sql(query).compute()
        else:
            if limit:
                df = dw.sql(f"SELECT * FROM {table} LIMIT {limit}").compute()
            else:
                df = dw.sql(f"SELECT * FROM {table}").compute()

        df_len = df.map_partitions(len).compute().sum()

        return (df, df_len)

    except Exception as e:

        traceback.print_exc()

        a = pd.DataFrame([f'unnable to query table {table}.'],
                         columns=['error'],
                        )
        return (a, len(a))

###############################################################################
# Dasboard layout
###############################################################################


###############################################################################
# Callbacks
###############################################################################

