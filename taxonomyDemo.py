analyzers = {
    "filter" : {
        "lay_to_legalise" : {
            "type" : "synonym",
            "synonyms" : [
                "dog catcher => idea_1234, idea_25",
                "animal control => idea_1234, idea_25",
                "spca officer => idea_1234, idea_25",
                "rabies shot => idea_5215, idea_25",
                "lyssaviruses => idea_5215, idea_25",
                "rabid dog => idea_5215, idea_25",
                "rabies vaccine => idea_5215, idea_25",
                "rabies vaccination => idea_5215, idea_25",
                "rabies vaccinations => idea_5215, idea_25",
                "rabies inoculation => idea_5215, idea_25",
                "health code => idea_936, idea_72"

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
