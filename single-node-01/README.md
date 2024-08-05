```
使用ik分詞器 單節點 elasticsearch伺服器
```

# 指令

```bash
# 查看節點訊息
curl http://localhost:9200/_cat/nodes?v

# 測試
curl http://localhost:9200


# 啟動pm2(一個個啟動)
pm2 start /usr/local/elasticsearch/js-pm2/bot_avnight.json
pm2 start /usr/local/elasticsearch/js-pm2/bot_jjkk.json
pm2 start /usr/local/elasticsearch/js-pm2/bot_inhand.json
pm2 start /usr/local/elasticsearch/js-pm2/bot_avnight-dev.json
pm2 start /usr/local/elasticsearch/js-pm2/bot_kissme.json
```

# 此專案使用方法

`安裝 必要工具 git gcc wget docker docker-compose pm2 golang nodejs`

```bash
# 安裝 git
yum install git -y

# 安裝 gcc
yum install gcc -y

# 安裝 wget
yum install wget -y
```

```bash
# 設置存儲庫
yum install -y yum-utils
yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# 驗證 Docker Engine 是否已正確安裝。
docker --version

# 安裝Docker-Compose
# 下載 Docker Compose 的當前穩定版本
# https://docs.docker.com/compose/release-notes/
curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 對二進製文件應用可執行權限
chmod +x /usr/local/bin/docker-compose

# 安裝 Docker Compose
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

# 驗證安裝：
docker-compose --version
```

`添加常用配置 docker 設定檔 daemon.json (沒有的話直接新增)`

```bash
vim /etc/docker/daemon.json
```

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "3"
  },
  "ipv6": true,
  "fixed-cidr-v6": "2001:db8:1::/64"
}
```

`使設定生效 重新載入 daemon 設定, 重啟 docker`

```bash
systemctl daemon-reload
systemctl restart docker
```

`安裝nvm nodejs pm2`

```bash
# 將內容加入環境變數文檔
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 安裝 NVM
bash /root/.nvm/install.sh

# 為了讓 NVM 生效，需要重新整理終端機的設定。
source ~/.bashrc

# 檢測是否安裝成功
nvm --version

# 安裝 nodejs
nvm install 16.16.0

# 將 Node.js 16.16.0 設置為默認版本
nvm alias default 16.16.0

# 安裝 pm2
npm install pm2@latest -g

# 安裝 pm2-logrotate (管理和維護應用程序的日誌檔案)
pm2 install pm2-logrotate
```

`安裝 Go`

```bash
# 下載 安裝包
wget https://golang.org/dl/go1.17.12.linux-amd64.tar.gz

# 解壓
tar -C /usr/local -xzf go1.17.12.linux-amd64.tar.gz

# 設定環境變數
export GOPATH=$HOME/go
export PATH=$PATH:$HOME/go/bin:$GOPATH/bin

# 重新整理終端機的設定。
source ~/.bashrc

# 檢測是否安裝成功
go version
```

```bash
cd /usr/local
git clone https://bitbucket.org/avnight/elasticsearch.git

# 進入 /usr/local/elasticsearch
mkdir es/data
mkdir es/logs

# 若 elasticsearch 啟動失敗 將es內的 data/ logs/ 權限開至最大
chmod 777 es/data/
chmod 777 es/logs/

# 啟動
docker-compose up -d

docker exec -ti elasticsearch bash

# 安裝ik分詞器 elasticsearch的版本和ik分詞器的版本需要保持一致
# Elasticsearch中預設的標準分詞器(analyze)對中文分詞不是很友好 因此需下載ik分詞器
# https://github.com/medcl/elasticsearch-analysis-ik/releases
cd /usr/share/elasticsearch/plugins
elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v7.13.3/elasticsearch-analysis-ik-7.13.3.zip

docker-compose restart elasticsearch
```

```bash
# 創建mapping (可以在後台用模板)
curl -X POST http://localhost:9200/index/_mapping?pretty -H 'Content-Type:application/json' -d'
{
	"properties": {
		"content": {
			"type": "text",
			"analyzer": "ik_max_word",
			"search_analyzer": "ik_smart"
		}
	}
}'
```

後台模板設定

http://{$host_ip}:5601/app/management/data/index_management/templates

`索引設置`

```json
{
  "index": {
    "number_of_shards": "5",
    "number_of_replicas": "0",
    "refresh_interval": "5m"
  }
}
```

`映射 - 動態模板`

```json
[
  {
    "strings": {
      "mapping": {
        "search_analyzer": "ik_max_word",
        "analyzer": "ik_max_word",
        "type": "text",
        "fields": {
          "keyword": {
            "ignore_above": 256,
            "type": "keyword"
          }
        }
      },
      "match_mapping_type": "string"
    }
  }
]
```

```bash
# clone monstache專案
git clone https://github.com/rwynn/monstache.git
cd monstache

# 版本
git checkout v6.7.10

# 安裝 monstache
go install
```

```json
// 修改設定檔 js-pm2/monstache_pm2.json
{
  "apps" : [{
    "name"        : "monstache", // pm2 app 名稱
    "script"      : "/root/go/bin/monstache",
    "watch"       : true,
    "cwd"         : "/path",
    "args"        : "-f /path/to/monstache/{name}_config.toml" // monstache 設定檔路徑
  }]
}
```

```toml
# 修改設定檔 monstache/config.toml
# connection settings
# monstache 設定檔

# connect to MongoDB using the following URL
mongo-url = "mongodb://username:password@host:port/?connect=direct"

# connect to the Elasticsearch REST API at the following node URLs
elasticsearch-urls = ["http://127.0.0.1:9200"]

# frequently required settings

# if you need to seed an index from a collection and not just listen and sync changes events
# you can copy entire collections or views from MongoDB to Elasticsearch
# direct-read-namespaces = ["mydb.mycollection", "db.collection", "test.test", "db2.myview"]
direct-read-namespaces = [""]

# if you want to use MongoDB change streams instead of legacy oplog tailing use change-stream-namespaces
# change streams require at least MongoDB API 3.6+ 3.6版本以上 實時同步
# if you have MongoDB 4+ you can listen for changes to an entire database or entire deployment
# in this case you usually don't need regexes in your config to filter collections unless you target the deployment.
# to listen to an entire db use only the database name.  For a deployment use an empty string.
# change-stream-namespaces = ["mydb.mycollection", "db.collection", "test.test"]
change-stream-namespaces = [""]

# additional settings

# if you don't want to listen for changes to all collections in MongoDB but only a few
# e.g. only listen for inserts, updates, deletes, and drops from mydb.mycollection
# this setting does not initiate a copy, it is only a filter on the change event listener
# namespace-regex = '^mydb\.mycollection$'

# compress requests to Elasticsearch
gzip = true
# generate indexing statistics
stats = true
# index statistics into Elasticsearch
index-stats = true
# use the following user name for Elasticsearch basic auth
# elasticsearch-user = "someuser"
# use the following password for Elasticsearch basic auth
# elasticsearch-password = "somepassword"
# use 4 go routines concurrently pushing documents to Elasticsearch
elasticsearch-max-conns = 4
# use the following PEM file to connections to Elasticsearch
# elasticsearch-pem-file = "/path/to/elasticCert.pem"
# validate connections to Elasticsearch
# elastic-validate-pem-file = true
# propogate dropped collections in MongoDB as index deletes in Elasticsearch
dropped-collections = false
# propogate dropped databases in MongoDB as index deletes in Elasticsearch
dropped-databases = false
# do not start processing at the beginning of the MongoDB oplog
# if you set the replay to true you may see version conflict messages
# in the log if you had synced previously. This just means that you are replaying old docs which are already
# in Elasticsearch with a newer version. Elasticsearch is preventing the old docs from overwriting new ones.
replay = false
# resume processing from a timestamp saved in a previous run
resume = true
# do not validate that progress timestamps have been saved
resume-write-unsafe = false
# override the name under which resume state is saved
resume-name = "default"
# use a custom resume strategy (tokens) instead of the default strategy (timestamps)
# tokens work with MongoDB API 3.6+ while timestamps work only with MongoDB API 4.0+
resume-strategy = 1
# exclude documents whose namespace matches the following pattern
# namespace-exclude-regex = '^mydb\.ignorecollection$'
# turn on indexing of GridFS file content
index-files = false
# turn on search result highlighting of GridFS content
# file-highlighting = true
# index GridFS files inserted into the following collections
file-namespaces = ["users.fs.files"]
# print detailed information including request traces
verbose = true
# enable clustering mode
# cluster-name = 'apollo'
# do not exit after full-sync, rather continue tailing the oplog
exit-after-direct-reads = false

# [[mapping]]
# namespace = "db.collection"
# index = ""

# 排除
direct-read-dynamic-exclude-regex = "(dbname1|dbname2).*(m3_u8|m3u8|account|.*log.*).*"

[[script]]
script="""
module.exports = function (doc, ns) {
  var index = "{名稱}-{日期}." + ns.split(".")[1];
  doc._meta_monstache = { index: index };
  return doc;
}
"""
```

`啟動 monstache 同步 mongo 建立索引`

```bash
pm2 start /usr/local/elasticsearch/js-pm2/bot_{產品名稱}.json
```

執行 pm2 startup 生成初始化系統腳本，然後執行 pm2 save 保存當前的 PM2 配置。

```bash
pm2 startup
pm2 save
```

# 使用 ssl

```bash
#!/bin/bash

# 檢查是否提供了主機名和 IP
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <host_name> <host_ip>"
  exit 1
fi

host_name=$1
host_ip=$2

# 生成 SSH 密鑰對
ssh-keygen -f ~/.ssh/$host_name -N ""

# 複製公鑰到遠程主機
ssh-copy-id -i ~/.ssh/$host_name.pub root@$host_ip

# 更新 SSH 配置文件
echo -e "\nHost $host_name\n    User root\n    HostName $host_ip\n    ServerAliveInterval 60\n    IdentityFile ~/.ssh/$host_name" >> ~/.ssh/config

echo "SSH configuration for $host_name ($host_ip) has been set up."
```

```bash
chmod +x setup_ssh.sh
```

```bash
./setup_ssh.sh jp-elasticsearch-dev 172.0.0.1
```

# logstash 用法

single-node-01/logstash/pipeline

修改 conf

編輯 .env LOGSTASH_CONF_PATH 變數

# mysql csv 匯出 建立索引

## 指令

匯出 csv 到 /var/lib/mysql-files

```bash
mysqldump --tab=/var/lib/mysql-files --fields-terminated-by=',' --fields-enclosed-by='"' --lines-terminated-by='\n' --no-create-info --user=yourusername --password=yourpassword yourdatabase yourtable
```

複製 CSV 文件

```bash
scp -r "$CSV_USER@$CSV_HOST:/var/lib/mysql-files" ./backup/csv
```

## 前置準備

參照 logstash/sample 內的 設定檔範本 建立到 logstash/pipeline

使用腳本自動化生成 SSH 密鑰對並配置 SSH 連接

```bash
chmod +x setup_ssh.sh
```

```bash
./setup_ssh.sh 主機名 主機IP
```

編輯環境變數

CSV_HOST

CSV_USER

```bash
vim .env
```

## 執行

備份 CSV 文件並重啟 Logstash

```bash
./backup_and_restart_logstash.sh
```

# mysql jdbc 插件連線 mysql 建立索引

## 前置準備

參照 logstash/sample 內的 設定檔範本 建立到 logstash/pipeline

使用腳本自動化生成 SSH 密鑰對並配置 SSH 連接

```bash
chmod +x setup_ssh.sh
```

```bash
./setup_ssh.sh 主機名 主機IP
```

```bash
chmod +x download_mysql_connector.sh
```

```bash
./download_mysql_connector.sh
```

## 執行

重啟 Logstash

```bash
docker-compose restart logstash
```
