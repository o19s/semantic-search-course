import scipy.sparse
import numpy
import sparsesvd

from collections import defaultdict


class StringIndexDict(object):
    """
    A 2-way dict-like object that only has functionality for getting and item.
    If you get with a string key, it will return the integer associated with that key.
    If you get with a integer key, it will return the string associated with that key.
    If you get an item that's currently not there, then the dict will return the next available
    integer (unique) and return that. If you call freeze on the dict, then nothing more
    can be added to it.
    """
    def __init__(self):
        self.currentIndex = -1
        self.stringDict = defaultdict(self._increment)
        self.indexDict = {}

    def _increment(self):
        self.currentIndex += 1
        self.indexDict[self.currentIndex] = self.keyInQuestion #kinda funky, but since this will always be single threaded, it's ok
        return self.currentIndex

    def __getitem__(self,key):
        self.keyInQuestion = key
        if isinstance(key,str):
            return self.stringDict[key]
        else :
            return self.indexDict[key]

    def size(self):
        return self.currentIndex + 1

    def freeze(self):
        #allow no more changes
        self.stringDict.default_factory = None



class TermDocCollection(object):
    def __init__(self,source=None,numTopics=10):
        self._docDict = StringIndexDict()
        self._termDict = StringIndexDict()
        self._termVectors = []
        self.numTopics = numTopics
        for termVector in source:
            self._termVectors.append( #append tuple of (docNum, {termNum_i,numberOccurrences_i})
                (
                    self._docDict[termVector[0]],
                    {self._termDict[k]:v for k,v in termVector[1].iteritems()}
                )
            )
        self._termDict.freeze()
        self._docDict.freeze()
        self.numTerms = self._termDict.size()
        self.numDocs = self._docDict.size()

        #memoized later:
        self._svd = None
        self._cscMatrix = None
        self._uPrime = None
        self._uStripped = None


    def _getCscMatrix(self):#compressed sparse column matrix
        if self._cscMatrix is not None:
            return self._cscMatrix
        # data and indices are parallel arrays,
        # data storing values (ie tf*idf) and indices storing values
        num_nnz, data, indices, indptr = 0, [], [], [0]
        for termVector in self._termVectors:
            newIndices = [i for i in termVector[1].keys()]
            newValues = [v for v in termVector[1].values()]
            indices.extend(newIndices)
            data.extend(newValues)
            num_nnz += len(newValues)
            indptr.append(num_nnz)
        data = numpy.asarray(data)
        indices = numpy.asarray(indices)
        # compressed sparse column matrix
        self._cscMatrix = scipy.sparse.csc_matrix((data, indices, indptr),
                shape=(self.numTerms, self.numDocs))
        return self._cscMatrix

    def _getSvd(self):
        if self._svd is not None:
            return self._svd
        self._svd = sparsesvd.sparsesvd(self._getCscMatrix(), self.numTopics)
        return self._svd

    def _getUprime(self):
        """ u combined with the strength of each topic (s)"""
        if self._uPrime is not None:
            return self._uPrime
        # u is
        u,s,v = self._getSvd()
        self._uPrime = numpy.dot(u.T,numpy.diag(s))
        return self._uPrime

    def getBlurredTerms(self,doc,cutoff):
        if isinstance(doc,str):
            doc = self._docDict[doc]
        uPrime = self._getUprime()
        _,_,v = self._getSvd()
        blurredField = numpy.dot(uPrime,v[:,doc])
        tokenIds = numpy.where(blurredField>cutoff)[0]
        tokens = [self._termDict[id] for id in tokenIds]
        return (self._docDict[doc], tokens)

    def _getStrippedUprime(self):
        #returns uPrime except that each word is only associated with their maximum
        #score in any topic (all other values are set to 0). This might give better
        #results for topic word lists
        if self._uStripped is not None:
            return self._uStripped
        uPrime = self._getUprime()
        uStripped = numpy.zeros(uPrime.shape)
        for termIndex in range(uPrime.shape[0]):
            maxIndex = numpy.argmax(uPrime[termIndex])
            uStripped[termIndex,maxIndex] = uPrime[termIndex,maxIndex]
        self._uStripped = uStripped
        return uStripped

    def getTopic(self,topicNum,cutoff,stripped=True):
        if stripped:
            u = self._getStrippedUprime()
        else:
            u = self._getUprime()

        return  [self._termDict[i]
                    for i in numpy.where(u.T[topicNum]>cutoff)[0]
                ]

    def getRelatedTerms(self,token,numTerms,tokens_only=True):
        uP = self._getUprime()
        termDict = self._termDict
        u,_,_ = self._getSvd()
        strength_and_indices = sorted( zip(numpy.dot(uP[termDict[token]],u),range(len(uP))) , reverse=True )
        method = 0
        if tokens_only:
            method = lambda i: termDict[i[1]]
        else:
            method = lambda i: (termDict[i[1]],i[0])
        return  [ method(i) for i in strength_and_indices[:numTerms] ]

