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