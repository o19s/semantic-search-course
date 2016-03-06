
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
    i = 500
    while len(resp['hits']['hits']) > 0:
        for doc in resp['hits']['hits']:
            yield doc['_id']
        print("Retrieved %s ids" % i)
        i += 500
        break
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

def say(a_list):
    print(" ".join(a_list))

if __name__ == "__main__":
    import pickleCache
    docIds = tvs = None
    try:
        docIds = pickleCache.fetch('docIds')
    except KeyError:
        docIds = [docId for docId in allCorpusDocs()]
        pickleCache.save('docIds')

    print("Fetching %s Term Vectors" % len(docIds))

    from lsi import TermDocCollection

    try:
        tvs = pickleCache.fetch('tvs')
    except KeyError:
        tvs = [tv for tv in allTermVectors]
        pickleCache.save('tws', tvs)

    tdc = TermDocCollection(tvs, numTopics=150)
    print("DEMO AUTOGEN SYNONYMS FOR DOCUMENTS")
    print("\n**star wars document**")
    import pdb; pdb.set_trace()
    say(tdc.getBlurredTerms(docIds[10])[1])

