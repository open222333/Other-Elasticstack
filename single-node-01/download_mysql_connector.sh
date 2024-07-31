# 讀取 .env 文件
source "$(dirname -- "$0")/.env"

# 檢查 MYSQL_CONNECTOR_VERSION 是否設置
if [ -z "$MYSQL_CONNECTOR_VERSION" ]; then
  echo "MYSQL_CONNECTOR_VERSION 未設置在 .env 文件中。"
  exit 1
fi

if [ -z "$MYSQL_CONNECTOR_PATH" ]; then
  echo "MYSQL_CONNECTOR_VERSION 未設置在 .env 文件中。"
  exit 1
fi


# 下載 MySQL Connector/J
wget https://dev.mysql.com/get/Downloads/Connector-J/mysql-connector-java-$MYSQL_CONNECTOR_VERSION.tar.gz

# 解壓縮文件
tar -xzf mysql-connector-java-$MYSQL_CONNECTOR_VERSION.tar.gz

# 移動 JAR 文件
mv mysql-connector-java-$MYSQL_CONNECTOR_VERSION/mysql-connector-java-$MYSQL_CONNECTOR_VERSION.jar /usr/share/logstash/jdbc_drivers/

# 刪除下載的壓縮檔
rm mysql-connector-java-$MYSQL_CONNECTOR_VERSION.tar.gz

# 刪除解壓縮後的目錄
rm -r mysql-connector-java-$MYSQL_CONNECTOR_VERSION
