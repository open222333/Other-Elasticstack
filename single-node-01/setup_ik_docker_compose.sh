# 集群
docker-compose exec elasticsearch elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v${STACK_VERSION}/elasticsearch-analysis-ik-${STACK_VERSION}.zip
# 重啟容器
docker-compose restart elasticsearch