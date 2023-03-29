import os
import json
import logging
import configparser

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

    lib_fname = config['LIB']['DATA']
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



