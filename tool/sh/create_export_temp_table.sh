#!/bin/bash

# 預設參數值
MYSQL_HOST="127.0.0.1"
MYSQL_PORT="3306"

COLUMN1=column1
COLUMN2=column2

# 處理命令行參數
while getopts "u:p:d:t:h:P:" opt; do
    case $opt in
        u) MYSQL_USER="$OPTARG" ;;
        p) MYSQL_PASSWORD="$OPTARG" ;;
        d) MYSQL_DATABASE="$OPTARG" ;;
        t) MYSQL_TABLE="$OPTARG" ;;
        h) MYSQL_HOST="$OPTARG" ;;
        P) MYSQL_PORT="$OPTARG" ;;
        *)
            echo "Usage: $0 -u <mysql_user> -p <mysql_password> -d <mysql_database> -t <mysql_table> [-h <mysql_host>] [-P <mysql_port>]"
            exit 1
            ;;
    esac
done

# 檢查必需的參數
if [ -z "$MYSQL_USER" ] || [ -z "$MYSQL_PASSWORD" ] || [ -z "$MYSQL_DATABASE" ] || [ -z "$MYSQL_TABLE" ]; then
    echo "Usage: $0 -u <mysql_user> -p <mysql_password> -d <mysql_database> -t <mysql_table> [-h <mysql_host>] [-P <mysql_port>]"
    exit 1
fi

EXPORT_PATH="/var/lib/mysql-files/${MYSQL_TABLE}_temp.txt"

# 確保導出路徑的目錄存在，並且 MySQL 有寫入權限
if [ ! -d "$(dirname "$EXPORT_PATH")" ]; then
    echo "Export path directory does not exist: $(dirname "$EXPORT_PATH")"
    exit 1
fi

# 創建新資料表
echo "只取 ${COLUMN1}, ${COLUMN2} 創建 temp 資料表"
mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -h $MYSQL_HOST -P $MYSQL_PORT -e "
CREATE TABLE ${MYSQL_DATABASE}.${MYSQL_TABLE}_temp AS
SELECT ${COLUMN1}, ${COLUMN2}
FROM ${MYSQL_DATABASE}.${MYSQL_TABLE};
"

if [ $? -ne 0 ]; then
    echo "發生錯誤 創建新資料表"
    exit 1
fi

# 匯出新資料表為 CSV 文件
echo "匯出 temp 資料表為 CSV 文件"
mysqldump --tab=/var/lib/mysql-files --fields-terminated-by=',' --fields-enclosed-by='"' --lines-terminated-by='\n' --no-create-info --user=$MYSQL_USER --password=$MYSQL_PASSWORD $MYSQL_DATABASE ${MYSQL_TABLE}_temp

if [ $? -ne 0 ]; then
    echo "發生錯誤 匯出 temp 資料表為 CSV 文件"
    exit 1
fi

# 刪除資料表
echo "刪除 temp 資料表"
mysql -u $MYSQL_USER -p$MYSQL_PASSWORD -h $MYSQL_HOST -P $MYSQL_PORT -e "
DROP TABLE ${MYSQL_DATABASE}.${MYSQL_TABLE}_temp;
"

if [ $? -ne 0 ]; then
    echo "發生錯誤 刪除 temp 資料表"
    exit 1
fi

echo "完成"
