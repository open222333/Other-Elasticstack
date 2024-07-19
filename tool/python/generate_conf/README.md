# 生成 logstash conf

複製 config.json.bak 成 config.json

讀取 JSON 配置文件中的多組資料庫和資料表。

對每個資料表，從 MySQL 取得其結構。

根據取得的結構動態生成 Logstash 配置。

將所有生成的 Logstash 配置合併成一個文件並輸出。