#!/bin/bash

# 讀取 .env 文件
source "$(dirname -- "$0")/.env"

# 檢查 STACK_VERSION 是否設置
if [ -z "$STACK_VERSION" ]; then
  echo "STACK_VERSION 未設置在 .env 文件中。"
  exit 1
fi

# 安裝插件
docker-compose exec elasticsearch elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v${STACK_VERSION}/elasticsearch-analysis-ik-${STACK_VERSION}.zip

# 檢查插件是否安裝成功
if [ $? -eq 0 ]; then
  echo 'Plugin installed successfully.'
else
  echo 'Plugin installation failed.'
  exit 1
fi

# 重啟 Elasticsearch 容器
docker-compose restart elasticsearch

# 檢查容器是否成功重啟
if [ $? -eq 0 ]; then
  echo 'Elasticsearch container restarted successfully.'
else
  echo 'Failed to restart Elasticsearch container.'
  exit 1
fi
