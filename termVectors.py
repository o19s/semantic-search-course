
from elasticsearch import Elasticsearch
es = Elasticsearch('http://localhost:9200')


def scoredFingerprint(terms):
    fp = {}
    for term, value in terms.items():
        fp[term] = float(value['term_freq']) / float(value['doc_freq'])
    return fp


def allCorpusDocs(index='stackexchange', doc_type='post', fields='Body.bigramed'):
    query = {
        "sort": ["_doc"],
        "size": 500
    }
    resp = es.search(index=index, doc_type=doc_type, scroll='1m', body=query)
    while len(resp['hits']['hits']) > 0:
        for doc in resp['hits']['hits']:
            yield doc['_id']
        scrollId = resp['_scroll_id']
        resp = es.scroll(scroll_id=scrollId, scroll='1m')


def termVectors(docIds, index='stackexchange', doc_type='post', field='Body.bigramed'):
    tvs = es.mtermvectors(ids=docIds, index=index, doc_type=doc_type, fields=field, term_statistics=True)
    for tv in tvs['docs']:
        try:
            yield (tv['_id'], scoredFingerprint(tv['term_vectors'][field]['terms']))
        except KeyError:
            pass


def groupEveryN(l, n=10):
    for i in range(0, len(l), n):
        yield l[i:i+n]


def allTermVectors(docIds):
    for docIdGroup in groupEveryN(docIds):
        for tv in termVectors(docIds=docIdGroup):
            yield tv


if __name__ == "__main__":
    docIds = [docId for docId in allCorpusDocs()]
    print("Fetching %s Term Vectors" % len(docIds))

    for tv in allTermVectors(docIds):
        print(tv)

