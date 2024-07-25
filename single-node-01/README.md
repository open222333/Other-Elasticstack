```
使用ik分詞器 單節點 elasticsearch伺服器
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
