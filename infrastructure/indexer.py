from elasticsearch import helpers, Elasticsearch


class ElasticIndexer:
    MAPPING = {"settings": {"mapping": {"total_fields": {"limit": "2000"}}}}

    def __init__(self, ip, port, user=None, password=None):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.es = self.__init_elastic()

    def __init_elastic(self):
        if self.user is not None and self.password is not None:
            es = Elasticsearch('{user}:{password}@{host}:{port}'.format(host=self.ip, port=self.port, user=self.user,
                                                                        password=self.password), timeout=60)
        else:
            es = Elasticsearch('{host}:{port}'.format(host=self.ip, port=self.port), timeout=60)
        return es

    def __create_index(self, index):
        try:
            self.es.indices.create(index, body=self.MAPPING)
        except:
            pass

    def index(self, index_name, data, bulk_size=500):
        """Index data to Elasticsearch DB

        Args:
            index_name: Name of the index in elasticsearch db
            data: list of jsons to index
            bulk_size: number of documents to index together
        Returns:
            None
        """
        self.__create_index(index_name)
        bulk_amount = int(len(data) / bulk_size if len(data) % bulk_size == 0 else len(data) / bulk_size + 1)
        for i in range(bulk_amount):
            try:
                helpers.bulk(self.es, data[i * bulk_size:(i + 1) * bulk_size], index=index_name)
            except IndexError as e:
                print(e)
            except Exception as e:
                print(e)


def get_indexer(args):
    indexer = None
    if args.host:
        # The connection to the DB, on this implementation we use elasticsearch
        indexer = ElasticIndexer(args.host, args.port, args.db_user, args.db_password)
    return indexer
