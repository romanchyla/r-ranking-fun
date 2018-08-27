from rfun.scoring import FlexibleScorer
import decimal

class MultiParameterEvaluator(object):
    def __init__(self, pPoints, docs, goldSet, kRange, bRange, docLenRange, normalizeWeight,fieldBoost):
        self.pPoints = pPoints
        self.docs = docs
        self.goldSet = goldSet
        self.kRange = kRange
        self.bRange = bRange
        self.docLenRange = docLenRange
        self.normalizeWeight = normalizeWeight
        self.fieldBoost = fieldBoost
        self.bestSet = None
        self.bestScore = 0.0
    
    def get_best(self):
        return self.bestSet
    
    def run(self, yield_per=1000):
        i = 0
        
        for k in self._xrange(*self.kRange):
            for b in self._xrange(*self.bRange):
                for dl in self._get_avg_doclen():
                    for normalize in self._get_normalize():
                        for doc_boost in self._get_doc_boost():
                            i += 1
                            
                            #print dict(k1=k, b=b, perdoc_boost=doc_boost, 
                            #                        idf_normalization=normalize,
                            #                        perfield_avgdoclen=dl)
                            scorer = FlexibleScorer(k1=k, b=b, perdoc_boost=doc_boost, 
                                                    idf_normalization=normalize,
                                                    perfield_avgdoclen=dl)
                            score = self._score(scorer)
                            if score > self.bestScore:
                                self.bestScore = score
                                self.bestSet = dict(k1=k, b=b, perdoc_boost=doc_boost, 
                                                    idf_normalization=normalize,
                                                    perfield_avgdoclen=dl)
                            if i % yield_per == 0:
                                yield (i, self.bestScore, self.bestSet)

        yield (i, self.bestScore, self.bestSet)
    
    def _xrange(self, x, y, step):
        while x < y:
            yield float(x)
            x += step
            
    def _score(self, scorer):
        hits = [0.0] * len(self.docs)
        i= 0
        for d in self.docs:
            hits[i] = (scorer.run(d['formula']), d['docid'])
            i+= 1
        hits.sort(key=lambda x: x[0], reverse=True)
        results = map(lambda x: x[1], hits)
        evaluator = AtPrecisionEvaluator(self.pPoints, self.goldSet, results)
        return evaluator.score()

    
    def _get_avg_doclen(self):
        if self.docLenRange:
            yield {} # TODO(rca): return smart dictionary that can decide based on a field
        else:
            yield None
        
    def _get_doc_boost(self):
        if self.fieldBoost:
            
            f = self.fieldBoost
            out = {}
            def getter(d):
                if f in d:
                    out[d['docid']] = d[f]
                else:
                    out[d['docid']] = 0.0 # or maybe ignore?
                        
            map(getter, self.docs)
            
            yield out
            yield {} # use no boost
            
        else:
            yield {}
        
    def _get_normalize(self):
        if self.normalizeWeight:
            for x in (True, False):
                yield x
        else:
            yield False
        

class AtPrecisionEvaluator(object):
    
    def __init__(self, p_points, golden_set, test_set):
        self.golden = golden_set
        self.tests = test_set
        self.p_points = p_points
        self.weights = self.compute_weight_factors()
    
    def score(self):
        #print 'weights', self.weights
        s = 0.0
        for i in range(len(self.weights)):
            x = self._score(self.p_points[i], self.weights[i])
            #print 'for p=', self.p_points[i], self.weights[i], x
            s += x
        return s
    
    def _score(self, p, weight):
        
        gs = self.get_golden_set_atp(p)
        ts = self.tests[0:p]
        overlap = float(len(gs.intersection(set(ts))))
        return (overlap / len(ts)) * weight
    
    def get_golden_set_atp(self, p):
        # if we cared about order we'd do
        # return set(self.golden[0:p])
        
        if isinstance(self.golden, list):
            self.golden = set(self.golden)
        return self.golden
    
    def compute_weight_factors(self):
        #num_boundary = max(len(self.golden), len(self.tests))
        considered = []
        for x in self.p_points:
            #if x <= num_boundary:
            considered.append(x)
        weights = []
        for i, p in zip(range(len(considered)), considered):
            weights.append(self.compute_weight(p, i, 1.0 - sum(weights)))
        
        if len(weights) > 1:
            weights[-1] = 1.0 - sum(weights[0:-1])
        else:
            weights[0] = 1.0
            
        return weights
            
    def compute_weight(self, p, rank, to_distribute):
        n = float(max(sum(self.p_points), len(self.golden)))
        #if p <= len(self.golden):
        #    return to_distribute
        return max(0.0, to_distribute * (1.0 - p/n))