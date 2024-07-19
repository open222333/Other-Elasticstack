from src.mysql_schema import generate_logstash_config, get_table_structure
import json
import os

# 獲取當前腳本文件所在的目錄
script_dir = os.path.dirname(os.path.realpath(__file__))
# 更改當前工作目錄到腳本所在目錄
os.chdir(script_dir)

config_file = 'config.json'

with open(config_file, 'r') as file:
    config_data = json.load(file)

all_configs = ""
for db_config in config_data["databases"]:
    host = db_config["host"]
    user = db_config["user"]
    password = db_config["password"]
    database = db_config["database"]
    tables = db_config["tables"]

    for table_name in tables:
        structure = get_table_structure(host, user, password, database, table_name)
        logstash_config = generate_logstash_config(structure, table_name)
        all_configs += logstash_config + "\n"

with open('output.conf', 'w') as f:
    f.write(all_configs)
