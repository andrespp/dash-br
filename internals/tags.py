import os
import json
import logging
import configparser
import pandas as pd

# config
CONFIG_FILE = './config.ini'

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

# logger
LOG_FORMAT = '%(levelname)s\t%(asctime)s:\t%(message)s'
logging.basicConfig(level = logging.DEBUG, format = LOG_FORMAT)
log = logging.getLogger(__name__)

def read_articles_from_json(art_fname, datasets_file):
    # read articles from json
    with open(art_fname, 'r') as f:
        articles = json.load(f)
        log.info(f'"{art_fname}" read. {len(articles)} entries.')

    # read datasets.json
    with open(datasets_file, 'r') as f:
        datasets = json.load(f)
        log.info(
            f'"{datasets_file} read. ' \
            f'{len(datasets["areas"])} areas, ' \
            f'{len(datasets["themes"])} themes, ' \
            f'{len(datasets["datasets"])} datasets.'
        )

    return articles, datasets

def lookup_datasets():
    """Lookup pandas df with all datasets defined
    """
    articles, datasets = read_articles_from_json(
        config['LIB']['ARTICLES'],
        config['LIB']['DATASETS']
    )

    ## lookup data articles.json
    art = pd.json_normalize(
        articles,
        record_path='datasets',
        meta=['name', 'year'],
        record_prefix='ds'
    )
    art.rename(
        index=str,
        columns={'ds0':'dataset', 'name':'article'},
        inplace=True
    )
    df = art[['dataset', 'article']].groupby(
            ['dataset']
        ).agg({'article':'count'}).reset_index()

    ## lookup data datasets.json

    # themes
    themes = datasets['themes']
    themes

    # repos
    repos = pd.json_normalize(datasets['repositories'])
    repos = repos[['id','name']]

    # datasets
    ds = pd.json_normalize(datasets['datasets'])
    ds = ds[['repository', 'id', 'name']]
    ds.rename(index=str, columns={'id':'dataset'}, inplace=True)

    df = pd.merge(
        ds,
        df,
        how='left',
        on='dataset',
    )
    df['article'].fillna(0, inplace=True)
    df['article'] = df['article'].apply(int)
    df = df.sort_values(by='repository')

    return df

def validate_classification(article, datasets):
    """Check if article entry is consistant to given datasets.

    This function checks if keys defined in 'datasets' are defined on 'article'
    and if its values are within those available on 'datasets'.

    Parameters
    ----------

        article | dictionary

        datasets | dictionary

    Return values
    -------------

        True if article meets datasets and false otherwise

    """
    is_valid = True

    # Check area
    try:
        for area in article['areas']:
            if area not in datasets['areas']:
                log.warning(f'"{article["name"]}": area "{area}" is invalid.')
                is_valid = False

    except KeyError:
        log.warning(f'"{article["name"]}": "areas" key not defined')
        is_valid = False

    # Check theme
    try:
        for theme in article['themes']:
            if theme not in datasets['themes']:
                log.warning(f'"{article["name"]}": theme "{theme}" is invalid.')
                is_valid = False

    except KeyError:
        log.warning(f'"{article["name"]}": "themes" key not defined')
        is_valid = False

    # Check datasets
    try:
        ds_ids = []
        for ds in datasets['datasets']:
            ds_ids.append(ds['id'])

        for ds in article['datasets']:
            if ds not in ds_ids:
                log.warning(f'"{article["name"]}": dataset "{ds}" is invalid.')
                is_valid = False

    except KeyError:
        log.warning(f'"{article["name"]}": "datasets" key not defined')
        is_valid = False

    return is_valid

if __name__ == "__main__":

    lib_fname = config['LIB']['ARTICLES']
    datasets_file = config['LIB']['DATASETS']

    # read articles from json
    with open(lib_fname, 'r') as f:
        articles = json.load(f)
        log.info(f'"{lib_fname}" read. {len(articles)} entries.')

    # read datasets.json
    with open(datasets_file, 'r') as f:
        datasets = json.load(f)
        log.info(
            f'"{datasets_file} read. ' \
            f'{len(datasets["areas"])} areas, ' \
            f'{len(datasets["themes"])} themes, ' \
            f'{len(datasets["datasets"])} datasets.'
        )

    # check article classification consistence
    for article in articles:
        validate_classification(article, datasets)

    # area consistence

    # theme consistence

    # main dificulties consistence

    # print statistics



