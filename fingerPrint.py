from elasticsearch import Elasticsearch
from sys import argv

es = Elasticsearch('http://localhost:9200')


class SparseVector():
    def __init__(self):
        self.counts = {}

    def add(self, keys):
        for key in keys:
            try:
                self.counts[key] += 1
            except KeyError:
                self.counts[key] = 1

    def ordered(self):
        countsAsTuples = [(key, value) for (key, value) in self.counts.items()]
        return sorted(countsAsTuples, key=lambda tup: tup[1], reverse=True)




sv = SparseVector()

for docId in argv[1:]:
    tvs = es.termvectors(id=docId, index='statedecoded', doc_type='law', fields='text.bigramed')
    import pdb; pdb.set_trace()
    fingerprint = tvs['term_vectors']['text.bigramed']['terms'].keys()
    sv.add(fingerprint)

asTups = sv.ordered()
for tup in asTups:
    print(tup)
