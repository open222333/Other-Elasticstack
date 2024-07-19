from configparser import ConfigParser
from argparse import ArgumentParser
from pprint import pformat
import logging
import json
import os

from src.elastic import ElasticQuery


parser = ArgumentParser()
parser.add_argument('-c', '--config', default='tool/python/conf/config.ini')
parser.add_argument('-i', '--index', type=str, required=True)
parser.add_argument('-q', '--query', default={"query": {"match_all": {}}})
parser.add_argument('-j', '--json', default=None)
parser.add_argument('-l', '--log_level', default='DEBUG')
args = parser.parse_args()

conf = ConfigParser()
conf.read(args.config)

logger = logging.getLogger('Elastic 測試')
logger.setLevel(args.log_level)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

HOST = conf.get('ELASTIC', 'HOST', fallback='localhost')
PORT = conf.getint('ELASTIC', 'PORT', fallback=9200)

es = ElasticQuery(HOST, PORT, args.index)
if args.json != None and os.path.exists(args.json):
    with open(args.json, 'r') as f:
        query = json.loads(f.read())
    logger.info(f'查詢條件: {query}')
    result = es.query(query)
    logger.info(f'{pformat(result)}')
else:
    if args.json == None:
        logger.info(f'{args.json} 未設定')
    elif os.path.exists(args.json) == False:
        logger.info(f'{args.json} 不存在')

    logger.info(f'查詢條件: {args.query}')
    result = es.query(args.query)
    logger.info(f'{pformat(result)}')
