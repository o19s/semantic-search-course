import requests
import json


def openLaws():
    data = ""
    try:
        f = open("statedecoded.json")
        data = f.read()
    except IOError:
        stateDecodedData ="https://storage.googleapis.com/quepid-sample-datasets/solr/statedecoded.json"
        resp = requests.get(stateDecodedData)
        print("GET %s Len %s" % (resp.status_code, len(resp.text)))
        f = open("statedecoded.json", "w")
        f.write(resp.text)
        data = resp.text
        f.close()
    return json.loads(data)

laws = openLaws()

def bulkAdds(laws, index='statedecoded'):
    print("Indexing %s Laws" % len(laws))
    for law in laws:
        print("indexing %s" % law['id'])
        yield {
                "_id": law['id'],
                "_index": index,
                '_type': 'document',
                '_op_type': 'index',
                'doc': law
              }


from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
es = Elasticsearch("http://localhost:9200")

bulk(es, bulkAdds(laws))
