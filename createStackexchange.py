settings = {
    "mappings": {
      "post": {
        "properties": {
            "body": {
              "type": "string",
            },
            "title": {
              "type": "string",
            }
        }
      }
    },
    "settings": {
      "index" : {
        "number_of_shards" : 1,
        "number_of_replicas" : 0
      },
    }
}

from elasticsearch import Elasticsearch, TransportError

try:
    es = Elasticsearch("http://localhost:9200")
    es.indices.delete(index='stackexchange', ignore=[400,404])
    es.indices.create(index='stackexchange', body=settings)
except TransportError as e:
    print(repr(e))
