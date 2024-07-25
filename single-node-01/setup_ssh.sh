#!/bin/bash

# 檢查是否設置了 host_name 和 host_ip 變數
if [ -z "$1" ] || [ -z "$2" ]; then
  echo "Usage: $0 <host_name> <host_ip>"
  exit 1
fi

host_name=$1
host_ip=$2

# 生成 SSH 密鑰對
ssh-keygen -f ~/.ssh/$host_name

# 複製公鑰到遠程主機
ssh-copy-id -i ~/.ssh/$host_name.pub root@$host_ip

# 檢查 ssh-copy-id 是否成功
if [ $? -eq 0 ]; then
  echo "公鑰已成功複製到遠程主機。"
else
  echo "公鑰複製失敗。請檢查連接或遠程主機設置。"
  exit 1
fi

# 將新配置追加到 ~/.ssh/config 文件末尾
echo -e "\nHost $host_name\n    User root\n    HostName $host_ip\n    ServerAliveInterval 60\n    IdentityFile ~/.ssh/$host_name" >> ~/.ssh/config

# 檢查配置是否成功添加
if [ $? -eq 0 ]; then
  echo "SSH 配置已成功添加到 ~/.ssh/config。"
else
  echo "SSH 配置添加失敗。"
  exit 1
fi
