from src.mysql_schema import generate_logstash_all_csv_config, get_table_structure, generate_logstash_csv_config, generate_logstash_all_jdbc_config
from argparse import ArgumentParser
import json
import os


parser = ArgumentParser()
parser.add_argument('-m', '--mode', choices=['all_csv', 'csv', 'jdbc'], default='csv')
parser.add_argument('-e', '--elastichost', default='elasticsearch')
args = parser.parse_args()

# 獲取當前腳本文件所在的目錄
script_dir = os.path.dirname(os.path.realpath(__file__))
# 更改當前工作目錄到腳本所在目錄
os.chdir(script_dir)

config_file = 'config.json'

with open(config_file, 'r') as file:
    config_data = json.load(file)

if args.mode == "all_csv":
    all_configs = ""
    for db_config in config_data["databases"]:
        host = db_config.get("host")
        port = int(db_config.get("port", 3306))
        user = db_config.get("user")
        password = db_config.get("password")
        database = db_config.get("database")
        tables = db_config.get("tables")

        for table_name in tables:
            structure = get_table_structure(host, user, password, database, table_name, port)
            logstash_config = generate_logstash_all_csv_config(structure, table_name)
            all_configs += logstash_config + "\n"

    with open('all_csv.conf', 'w') as f:
        f.write(all_configs)
        
elif args.mode == "csv":
    for db_config in config_data["databases"]:
        host = db_config.get("host")
        port = int(db_config.get("port", 3306))
        user = db_config.get("user")
        password = db_config.get("password")
        database = db_config.get("database")
        tables = db_config.get("tables")

        for table_name in tables:
            structure = get_table_structure(host, user, password, database, table_name, port)
            logstash_config = generate_logstash_csv_config(structure, table_name, elastic_host=args.elastichost)

            with open(f'{table_name}.conf', 'w') as f:
                f.write(logstash_config)

elif args.mode == "jdbc":
    all_configs = ""
    for db_config in config_data["databases"]:
        host = db_config.get("host")
        port = int(db_config.get("port", 3306))
        user = db_config.get("user")
        password = db_config.get("password")
        database = db_config.get("database")
        tables = db_config.get("tables")

        jdbc_url = f"jdbc:mysql://{host}:{port}/{database}"

        structures = {}
        for table_name in tables:
            structure = get_table_structure(host, user, password, database, table_name, port)
            structures[table_name] = structure

        logstash_config = generate_logstash_all_jdbc_config(
            structures,
            jdbc_url,
            user,
            password,
            elastic_host=args.elastichost
        )

    with open('jdbc.conf', 'w') as f:
        f.write(logstash_config)
