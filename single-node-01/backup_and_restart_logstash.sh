#!/bin/bash

# 讀取 .env 文件
source "$(dirname -- "$0")/.env"

# 檢查 $CSV_USER 和 $CSV_HOST 是否為空
if [ -z "$CSV_USER" ] || [ -z "$CSV_HOST" ]; then
  echo "Error: CSV_USER and CSV_HOST must be set in the .env file."
  exit 1
fi

# 複製 CSV 文件
scp -r "$CSV_USER@$CSV_HOST:/var/lib/mysql-files" ./backup/csv

# 重啟 logstash
docker-compose restart logstash
