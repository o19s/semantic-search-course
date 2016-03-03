
from elasticsearch import Elasticsearch
from sys import argv

es = Elasticsearch('http://localhost:9200')


class SparseVector():
    def __init__(self):
        self.counts = {}

    def add(self, fp):
        for term,score in fp.items():
            try:
                self.counts[term] += score
            except KeyError:
                self.counts[term] = score

    def ordered(self):
        countsAsTuples = [(key, value) for (key, value) in self.counts.items()]
        return sorted(countsAsTuples, key=lambda tup: tup[1], reverse=True)




sv = SparseVector()

def scoredFingerprint(terms):
    fp = {}
    for term, value in terms.items():
        fp[term] = value['term_freq'] / (value['doc_freq'])
    return fp



for docId in argv[1:]:
    tvs = es.termvectors(id=docId, index='statedecoded', doc_type='law', fields='text.bigramed', term_statistics=True)
    fingerprint = scoredFingerprint(tvs['term_vectors']['text.bigramed']['terms'])
    sv.add(fingerprint)

asTups = sv.ordered()
for tup in asTups:
    print(tup)
