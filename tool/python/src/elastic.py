from elasticsearch import Elasticsearch


class ElasticQuery:

    def __init__(self, host="localhost", port=9200, index_name=None) -> None:
        # 建立Elasticsearch客戶端
        self.es = Elasticsearch([{'host': host, 'port': port}])
        self.index_name = index_name
        self.response = None

    def set_index_name(self, index_name):
        self.index_name = index_name

    def set_query(self, query):
        """
        search_query = {
            "query": {
                "match_all": {}
            }
        }

        Args:
            query (_type_): _description_
        """
        self.query = query

    def query(self, index: str, query):
        """_summary_

        Args:
            index (str): 索引
            query (_type_): 搜尋
        """
        self.response = self.es.search(index=index, body=query)
        return self.response

    def list_result(self):
        """回傳 串列結果

        Returns:
            _type_: _description_
        """

        if self.response != None:
            # 打印搜尋結果
            return [hit for hit in self.response['hits']['hits']]
