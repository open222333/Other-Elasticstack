from configparser import ConfigParser
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument('-c', '--config', default='tool/python/conf/config.ini')
args = parser.parse_args()
conf = ConfigParser(args.config)
conf.read()

