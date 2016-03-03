analyzers = {
    "filter" : {
        "lay_to_legalise" : {
            "type" : "synonym",
            "synonyms" : [
                "dog catcher => idea_1234",
                "animal control => idea_1234"
            ]
        },
        "bigram_filter": {
                "type": "shingle",
                "max_shingle_size":2,
                "min_shingle_size":2,
                "output_unigrams":"false"
        }
    },
    "analyzer": {
        "legalise": {
            "tokenizer": "standard",
            "filter": ["lowercase"]
        },
        "legalise_bigrams": {
            "tokenizer": "standard",
            "filter": ["lowercase", "bigram_filter"]
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
              "fields": {
                "bigramed": {
                  "term_vector": "with_positions_offsets_payloads",
                  "type": "string",
                  "analyzer": "legalise_bigrams"
                }
              }

            },
            "catch_line": {
              "type": "string",
              "analyzer": "legalise",
              "fields": {
                "bigramed": {
                  "term_vector": "with_positions_offsets_payloads",
                  "type": "string",
                  "analyzer": "legalise_bigrams"
                }
              }
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
