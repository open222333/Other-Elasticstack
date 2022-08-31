# 集群
docker-compose exec es01 elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v${STACK_VERSION}/elasticsearch-analysis-ik-${STACK_VERSION}.zip
docker-compose exec es02 elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v${STACK_VERSION}/elasticsearch-analysis-ik-${STACK_VERSION}.zip
docker-compose exec es03 elasticsearch-plugin install https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v${STACK_VERSION}/elasticsearch-analysis-ik-${STACK_VERSION}.zip
# 重啟容器
docker-compose restart es01
docker-compose restart es02
docker-compose restart es03