from elasticsearch import Elasticsearch
import logging


class ElasticQuery:

    def __init__(self, host="localhost", port=9200, index_name=None, log_level="DEBUG", scheme='http') -> None:
        self.logger = logging.getLogger('ElasticQuery')
        self.logger.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # 建立Elasticsearch客戶端
        try:
            self.es = Elasticsearch([{'host': host, 'port': port, 'scheme': scheme}])
        except Exception as err:
            self.logger.error(f'{err}, host: {host}, port: {port}', exc_info=True)

        self.index_name = index_name
        self.response = None

    def set_index_name(self, index_name):
        self.index_name = index_name

    def query(self, query):
        """_summary_

        Args:
            query (_type_): 搜尋
        """
        try:
            self.response = self.es.search(index=self.index_name, body=query)
        except Exception as err:
            self.logger.error(f'{err}, index: {self.index_name}, query: {query}', exc_info=True)
        return self.response

    def list_result(self):
        """回傳 串列結果

        Returns:
            _type_: _description_
        """

        if self.response != None:
            # 打印搜尋結果
            return [hit for hit in self.response['hits']['hits']]
