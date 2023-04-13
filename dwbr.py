import os
import dask.dataframe as dd
from dask_sql import Context

def load_dw(datadir, verbose=True):
    """Build dask-sql context

    Parameters
    ----------

        datadir | string

    Returns
    -------

        dasq_sql Context

    """
    if verbose:
        print('Loading parquet tables: ', end='', flush=True)

    # Create Context
    c = Context()

    # Lookup tables
    tables = []
    with os.scandir(datadir) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_dir():
                tables.append(entry.name)
    if verbose: print(f'{tables}', end='', flush=True)

    # Load tables
    for table in tables:
        c.create_table(
            table,
            dd.read_parquet(os.path.join(datadir, table))
        )

    if verbose:
        print('...ok', flush=True)

    return c
