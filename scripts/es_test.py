from elasticsearch import Elasticsearch
import certifi

# connect es
es = Elasticsearch(hosts=['search-tweet2map-lldav6drz4p5byukwym7dplysa.us-west-2.es.amazonaws.com'],
                   port=443, use_ssl=True, verify_certs=True, ca_certs=certifi.where())
orig_msg = {'name': 'he', 'age': 18, 'haha': [1, 2]}
es.create(index='test-index', doc_type='test-type', body=orig_msg)
