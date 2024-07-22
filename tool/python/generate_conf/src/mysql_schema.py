import mysql.connector


def get_table_structure(host, user, password, database, table_name, port=3306):
    """
    從 MySQL 資料庫中獲取指定表的結構

    Args:
        host (str): 資料庫主機名或 IP 地址
        port (int): 預設 3306
        user (str): 連接資料庫的用戶名
        password (str): 連接資料庫的密碼
        database (str): 資料庫名稱
        table_name (str): 表名稱

    Returns:
        list: 包含表結構的列表，每個元素是一個包含欄位名稱和欄位類型的元組
    """
    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )
    cursor = conn.cursor()
    query = f"DESCRIBE {table_name}"
    cursor.execute(query)
    table_structure = cursor.fetchall()
    cursor.close()
    conn.close()
    return table_structure


def generate_logstash_all_csv_config(structure, table_name, elastic_host="localhost", csv_path="/usr/mysql_backup/csv/"):
    """
    根據表結構生成 Logstash 配置

    Args:
        structure (list): 表結構的列表，每個元素是一個包含欄位名稱和欄位類型的元組
        table_name (str): 表名稱
        elastic_host (str): elastic 主機，預設 localhost

    Returns:
        str: 生成的 Logstash 配置
    """
    input_config = f"""
input {{
  file {{
    path => "{csv_path}{table_name}.txt"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => plain {{
      charset => "UTF-8"
    }}
    add_field => {{ "[@metadata][source_file]" => "%{{path}}" }}
  }}
}}
"""

    filter_config = f"""
filter {{
  mutate {{
    gsub => [
      "[@metadata][source_file]", "/path/to/csv_files/", "",
      "[@metadata][source_file]", ".txt", ""
    ]
  }}

  if [@metadata][source_file] == "{table_name}" {{
    csv {{
      separator => ","
      columns => [{', '.join([f'"{col[0]}"' for col in structure])}]
      quote_char => '"'
    }}
    mutate {{
      convert => {{
"""

    for column in structure:
        field_name = column[0]
        field_type = column[1]

        if "int" in field_type:
            logstash_type = "integer"
        elif "char" in field_type or "text" in field_type:
            logstash_type = "string"
        elif "datetime" in field_type or "timestamp" in field_type:
            logstash_type = "date"
        elif "float" in field_type or "double" in field_type or "decimal" in field_type:
            logstash_type = "float"
        else:
            logstash_type = "string"

        filter_config += f'        "{field_name}" => "{logstash_type}",\n'

    filter_config += """
      }
    }
  }
}
"""

    output_config = f"""
output {{
  elasticsearch {{
    hosts => ["http://{elastic_host}:9200"]
    index => "index_{table_name}"
    document_id => "%{{id}}"
  }}
  stdout {{ codec => rubydebug }}
}}
"""

    logstash_config = input_config + filter_config + output_config
    return logstash_config


def generate_logstash_all_jdbc_config(structures, jdbc_url, jdbc_user, jdbc_password, elastic_host="localhost", jar_path="/usr/share/logstash/jdbc_drivers/mysql-connector-java-8.0.23.jar"):
    """
    生成 Logstash JDBC 插件配置文件

    structures = {
        "users": [
            ("id", "int(11)"),
            ("name", "varchar(255)"),
            ("email", "varchar(255)"),
            ("created_at", "datetime")
        ],
        "orders": [
            ("order_id", "int(11)"),
            ("user_id", "int(11)"),
            ("product", "varchar(255)"),
            ("amount", "decimal(10,2)"),
            ("order_date", "datetime")
        ]
    }

    Args:
        structures (dict): 一個包含表名和其結構的字典。字典的鍵是表名，值是表結構的列表。
                          表結構的列表中每個元素是一個包含欄位名稱和欄位類型的元組。
        jdbc_url (str): JDBC 連接 URL，用於連接 MySQL 資料庫。例如 "jdbc:mysql://host:port/database"。
        jdbc_user (str): JDBC 連接用戶名。
        jdbc_password (str): JDBC 連接密碼。
        elastic_host (str): elastic 主機，預設 localhost。

    Returns:
        str: 生成的 Logstash 配置文件內容。
    """
    input_config = """
input {
"""
    for table_name, structure in structures.items():
        input_config += f"""
  jdbc {{
    jdbc_driver_library => "{jar_path}"
    jdbc_driver_class => "com.mysql.jdbc.Driver"
    jdbc_connection_string => "{jdbc_url}"
    jdbc_user => "{jdbc_user}"
    jdbc_password => "{jdbc_password}"
    statement => "SELECT * FROM {table_name}"
    add_field => {{ "[@metadata][table]" => "{table_name}" }}
  }}
"""
    input_config += """
}
"""

    filter_config = """
filter {
"""
    for table_name, structure in structures.items():
        filter_config += f"""
  if [@metadata][table] == "{table_name}" {{
    mutate {{
      convert => {{
"""

        for column in structure:
            field_name = column[0]
            field_type = column[1]

            if "int" in field_type:
                logstash_type = "integer"
            elif "char" in field_type or "text" in field_type:
                logstash_type = "string"
            elif "datetime" in field_type or "timestamp" in field_type:
                logstash_type = "date"
            elif "float" in field_type or "double" in field_type or "decimal" in field_type:
                logstash_type = "float"
            else:
                logstash_type = "string"

            filter_config += f'        "{field_name}" => "{logstash_type}"\n'

        filter_config += """
      }
    }
  }
"""
    filter_config += """
}
"""

    output_config = f"""
output {{
  elasticsearch {{
    hosts => ["http://{elastic_host}:9200"]
    index => "index_%{{[@metadata][table]}}"
    document_id => "%{{id}}"
  }}
  stdout {{ codec => rubydebug }}
}}
"""

    logstash_config = input_config + filter_config + output_config
    return logstash_config


def generate_logstash_csv_config(structure, table_name, elastic_host="localhost", csv_path="/usr/mysql_backup/csv/"):
    """
    根據表結構生成 Logstash 配置

    Args:
        structure (list): 表結構的列表，每個元素是一個包含欄位名稱和欄位類型的元組
        table_name (str): 表名稱
        elastic_host (str): elastic 主機，預設 localhost

    Returns:
        str: 生成的 Logstash 配置
    """
    # Input 部分
    input_config = f"""
input {{
  file {{
    path => "{csv_path}{table_name}.txt"
    start_position => "beginning"
    sincedb_path => "/dev/null"
    codec => plain {{
      charset => "UTF-8"
    }}
  }}
}}
"""

    # Filter 部分
    filter_config = f"""
filter {{
  csv {{
    separator => ","
    columns => [{', '.join([f'"{col[0]}"' for col in structure])}]
    quote_char => '"'
  }}

  mutate {{
    convert => {{
"""

    # 添加 convert 配置
    for column in structure:
        field_name = column[0]
        field_type = column[1]

        if "int" in field_type:
            logstash_type = "integer"
        elif "char" in field_type or "text" in field_type:
            logstash_type = "string"
        elif "datetime" in field_type or "timestamp" in field_type:
            logstash_type = "date"
        elif "float" in field_type or "double" in field_type or "decimal" in field_type:
            logstash_type = "float"
        else:
            logstash_type = "string"

        filter_config += f'      "{field_name}" => "{logstash_type}",\n'

    filter_config += """
    }
  }
}
"""

    # Output 部分
    output_config = f"""
output {{
  elasticsearch {{
    hosts => ["http://{elastic_host}:9200"]
    index => "{table_name}"
    document_id => "%{{{table_name}_id}}"
  }}
  stdout {{ codec => rubydebug }}
}}
"""

    # 合併所有部分並返回
    logstash_config = input_config + filter_config + output_config
    return logstash_config
