analyzers = {
    "filter" : {
        "lay_to_legalise" : {
            "type" : "synonym",
            "synonyms" : [
                "dog catcher => idea_1234",
                "animal control => idea_1234"
            ]
        }
    },
    "analyzer": {
        "legalise": {
            "tokenizer": "standard",
            "filter": ["lowercase", "lay_to_legalise"]
        }
    }
}




settings = {
    "mappings": {
      "law": {
        "properties": {
            "text": {
              "type": "string",
              "analyzer": "legalise",
              "term_vector": "with_positions_offsets_payloads",

            },
            "catch_line": {
              "type": "string",
              "analyzer": "legalise",
              "term_vector": "with_positions_offsets_payloads",
            }
        }
      }
    },
    "settings": {
      "index" : {
        "number_of_shards" : 1,
        "number_of_replicas" : 0,
        "analysis": analyzers
      },
    }
}

from elasticsearch import Elasticsearch, TransportError

try:
    es = Elasticsearch("http://localhost:9200")
    es.indices.delete(index='statedecoded', ignore=[400,404])
    es.indices.create(index='statedecoded', body=settings)
except TransportError as e:
    print(repr(e))
