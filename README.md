# Other-Elasticstack

使用 Docker Compose 建立 Elasticsearch + Kibana 練習環境，提供三種部署模式。

## 目錄

- [專案說明](#專案說明)
- [模式說明](#模式說明)
  - [single-node-01](#single-node-01)
  - [cluster_01](#cluster_01)
  - [cluster_02](#cluster_02)
- [執行流程](#執行流程)
- [使用方法](#使用方法)
- [建議注意事項](#建議注意事項)
- [生產環境建議設定](#生產環境建議設定)
- [參考資料](#參考資料)

---

## 專案說明

```
Elasticsearch 是一個基於 Lucene 庫的搜尋引擎。
提供分散式、支援多租戶的全文搜尋引擎，具有 HTTP Web 介面和無模式 JSON 文件。

Kibana 是免費且開放的用戶界面，能夠對 Elasticsearch 數據進行可視化，
並在 Elastic Stack 中進行導航。
```

---

## 模式說明

### single-node-01

單節點模式，搭配 Logstash + Monstache，適合開發與資料同步練習。

| 元件 | 說明 |
|---|---|
| Elasticsearch | 單節點，port 9200 |
| Kibana | 視覺化 UI，port 5601 |
| Monstache | MongoDB Change Stream → Elasticsearch 即時同步 |
| Logstash | JDBC（MySQL）/ CSV 匯入 |
| pm2 | 管理 Monstache 進程 |

### cluster_01

3 節點 ES 叢集 + Kibana，無 SSL，適合叢集架構練習。

| 節點 | Port |
|---|---|
| es01 | 9200, 9300 |
| es02 | 9201, 9301 |
| es03 | 9202, 9302 |
| Kibana | 5601 |

每個節點有獨立的 `elasticsearch.yml` 設定檔。

### cluster_02

3 節點 ES 叢集 + Kibana + SSL（xpack.security），生產環境級別安全設定。

| 元件 | 說明 |
|---|---|
| setup service | 自動產生 CA 和節點憑證 |
| Elasticsearch | HTTPS 9200 |
| Kibana | HTTP 5601 |

需要在 `.env` 設定以下變數：

```env
ELASTIC_PASSWORD=your_password
KIBANA_PASSWORD=your_kibana_password
STACK_VERSION=7.13.3
```

---

## 執行流程

### single-node-01 流程

```
[MongoDB]
    |
    | Change Stream (實時)
    v
[Monstache] <-- pm2 管理
    |
    | 索引資料
    v
[Elasticsearch :9200]
    |
    v
[Kibana :5601]  <-- 視覺化查詢

[MySQL / CSV]
    |
    | JDBC / File Input
    v
[Logstash]
    |
    v
[Elasticsearch :9200]
```

### cluster_01 / cluster_02 流程

```
Docker Compose up
    |
    +--> es01 :9200 ---+
    |                  |
    +--> es02 :9201 ---+--> ES Cluster (3 nodes)
    |                  |
    +--> es03 :9202 ---+
    |
    +--> Kibana :5601 --> 連接 ES Cluster

[cluster_02 額外步驟]
    setup service
        |
        |--> 產生 CA 憑證
        |--> 產生各節點憑證
        v
    ES HTTPS + xpack.security 啟用
```

---

## 使用方法

### 啟動服務

```bash
# 選擇模式目錄後啟動
cd single-node-01
docker compose up -d

cd cluster_01
docker compose up -d

cd cluster_02
# 先設定 .env 後啟動
cp .env.example .env
# 編輯 .env 填入密碼與版本
docker compose up -d
```

### 測試連線

```bash
# 測試 Elasticsearch
curl http://localhost:9200

# 查看叢集節點
curl http://localhost:9200/_cat/nodes?v

# cluster_02 需帶入帳密
curl -u elastic:your_password https://localhost:9200 --cacert certs/ca/ca.crt
```

### 安裝 IK 中文分詞器

```bash
# 進入容器
docker exec -ti elasticsearch bash

# 安裝 IK 分詞器（版本需與 Elasticsearch 一致）
cd /usr/share/elasticsearch/plugins
elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v7.13.3/elasticsearch-analysis-ik-7.13.3.zip

# 重啟容器
docker compose restart elasticsearch
```

### 建立含中文分詞的 Mapping

```bash
curl -XPOST http://localhost:9200/index/_mapping?pretty \
  -H 'Content-Type:application/json' \
  -d '{
    "properties": {
      "content": {
        "type": "text",
        "analyzer": "ik_max_word",
        "search_analyzer": "ik_smart"
      }
    }
  }'
```

### 設定 Monstache（single-node-01）

```bash
# 安裝 pm2
nvm install 16.16.0
nvm alias default 16.16.0
npm install pm2@latest -g

# 在 CentOS 上安裝 Go
wget https://golang.org/dl/go1.17.1.linux-amd64.tar.gz
tar -C /usr/local -xzf go1.17.1.linux-amd64.tar.gz
export PATH=$PATH:/usr/local/go/bin
export GOPATH=$HOME/go

# 安裝 Monstache
git clone https://github.com/rwynn/monstache.git
cd monstache
git checkout <branch-or-tag-to-build>
go install

# 啟動 Monstache
pm2 start /path/to/js-pm2/monstache_pm2.json
```

Monstache pm2 設定（`js-pm2/monstache_pm2.json`）：

```json
{
  "apps": [{
    "name": "monstache",
    "script": "/root/go/bin/monstache",
    "watch": true,
    "cwd": "/path",
    "args": "-f /path/to/monstache/config.toml"
  }]
}
```

Monstache 設定檔（`monstache/config.toml`）關鍵參數：

```toml
mongo-url = "mongodb://username:password@host:port/?connect=direct"
elasticsearch-urls = ["http://127.0.0.1:9200"]

# 初次全量同步
direct-read-namespaces = ["mydb.mycollection"]

# 即時同步（需 MongoDB 3.6+）
change-stream-namespaces = ["mydb.mycollection"]

gzip = true
resume = true
resume-strategy = 1
exit-after-direct-reads = false
```

---

## 建議注意事項

1. **IK 分詞器版本必須與 Elasticsearch 版本完全一致**，否則啟動會失敗。
2. **cluster_02 的 `.env` 檔案不要提交到版本控制**，內含敏感密碼。
3. **cluster_01 / cluster_02 的 `data/` 和 `logs/` 目錄需開放適當權限**，否則容器啟動失敗。
4. **Monstache 使用 Change Stream 需要 MongoDB 3.6+ 並且 MongoDB 必須是 Replica Set 架構**。
5. **切換 Monstache config 後需重啟 pm2 進程**，設定才會生效。
6. 預設 Elasticsearch 不啟用安全認證，若需對外開放請使用 cluster_02 模式。

---

## 生產環境建議設定

### 系統層級

```bash
# MMapFs 配置（需高於 262144）
sysctl -w vm.max_map_count=262144

# 設定 swappiness（緊急時仍可使用 swap）
sysctl -w vm.swappiness=1

# 永久設定（重啟後保留）
vim /etc/sysctl.conf
# 加入：
# vm.max_map_count = 262144
# vm.swappiness = 1

# 修改檔案描述符限制
vim /etc/security/limits.conf
# 加入：
# * soft nofile 65536
# * hard nofile 65536
# * soft memlock unlimited
# * hard memlock unlimited

# 關閉 swap（臨時）
swapoff -a
```

### systemd override

```bash
# /etc/systemd/system/elasticsearch.service.d/override.conf
[Service]
LimitMEMLOCK=infinity

# 重新載入
systemctl daemon-reload
```

### JVM 設定（`jvm.options.d/` 目錄下新增檔案）

```
# 設定為機器記憶體的一半
-Xms16g
-Xmx16g
```

### elasticsearch.yml 關鍵設定

```yaml
bootstrap.memory_lock: true
network.host: 0.0.0.0
http.port: 9200
discovery.zen.minimum_master_nodes: 2
action.destructive_requires_name: true
```

---

## 參考資料

- [Elasticsearch WIKI](https://zh.wikipedia.org/zh-tw/Elasticsearch)
- [Kibana 介紹](https://www.elastic.co/cn/kibana/)
- [Elasticsearch Guide - 官方教學文檔](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [elasticsearch-analysis-ik - IK 分詞器 GitHub](https://github.com/medcl/elasticsearch-analysis-ik)
- [elasticsearch-analysis-ik - 所有版本下載](https://github.com/medcl/elasticsearch-analysis-ik/releases)
- [docker-compose 安裝 elasticsearch 及 kibana](https://www.cnblogs.com/chenyuanbo/p/16183304.html)
- [docker-compose 快速部署 elasticsearch-8.x 集群+kibana](https://blog.csdn.net/boling_cavalry/article/details/125232858)
- [生產環境的 ElasticSearch 安裝指南](https://iter01.com/74792.html)
- [理解 ElasticSearch 工作原理](https://www.jianshu.com/p/52b92f1a9c47)
