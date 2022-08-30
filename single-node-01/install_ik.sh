# 容器es
docker exec -it es /bin/bash

# 使用bin 設計的下載elasticsearch-plugin install 安全名前
bin/elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v${STACK_VERSION}/elasticsearch-analysis-ik-${STACK_VERSION}.zip

# 重啟容器
docker restart es