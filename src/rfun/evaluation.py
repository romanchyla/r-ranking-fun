from rfun.scoring import FlexibleScorer, LuceneBM25Scorer
import decimal
import heapq
import itertools

class MultiParameterEvaluator(object):
    def __init__(self, 
                 pPoints, 
                 docs, 
                 goldSet, 
                 kRange=None, 
                 bRange=None, 
                 docLenRange=None, 
                 normalizeWeight=None,
                 fieldBoost=None, 
                 constRanges=None,
                 num_results=5):
        
        self.pPoints = pPoints
        self.docs = docs
        self.goldSet = goldSet
        self.kRange = kRange
        self.bRange = bRange
        self.docLenRange = docLenRange
        self.normalizeWeight = normalizeWeight
        self.fieldBoost = fieldBoost
        self.constRanges = constRanges
        self._constRanges = None
        self._optimize_constant_search_space()
        
        self.num_results = num_results
        self.heap = []

    
    def run(self, yield_per=1000):
        i = 0
        heap = self.heap
        
        # yes, crazy... ;-)
        for k in self._xrange(*self.kRange):
            for b in self._xrange(*self.bRange):
                for dl in self._get_avg_doclen():
                    for normalize in self._get_normalize():
                        for doc_boost in self._get_doc_boost():
                            for const_factor in self._get_const_ranges():
                                i += 1
                                
                                #print dict(k1=k, b=b, perdoc_boost=doc_boost, 
                                #                        idf_normalization=normalize,
                                #                        perfield_avgdoclen=dl)
                                scorer = FlexibleScorer(k1=k, b=b, perdoc_boost=doc_boost, 
                                                        idf_normalization=normalize,
                                                        perfield_avgdoclen=dl,
                                                        consts=const_factor)
                                score = self._score(scorer)
                                item = (score, dict(k1=k, b=b, perdoc_boost=doc_boost, 
                                                        idf_normalization=normalize,
                                                        perfield_avgdoclen=dl,
                                                        consts=const_factor))
                                if len(heap) >= self.num_results:
                                    heapq.heappushpop(heap, item)
                                else:
                                    heapq.heappush(heap, item)
                                
                                if i % yield_per == 0:
                                    yield (i, self.get_results(1))
        # final notification
        yield (i, self.get_results(1))

    
    def get_size(self):
        """Returns the number of parameters that are going to be tested"""
        k = self.kRange and int((self.kRange[1] - self.kRange[0]) / self.kRange[2]) or 1
        b = self.bRange and int((self.bRange[1] - self.bRange[0]) / self.bRange[2]) or 1
        dl = self.docLenRange and int((self.docLenRange[1] - self.docLenRange[0]) / self.docLenRange[2]) or 1
        r = k * b * dl
        if self.normalizeWeight:
            r *= 2
        if self.fieldBoost:
            r *= 2
        if self._constRanges and len(self._constRanges['fields']):
            x = self._constRanges['range']
            r *= int((x[1] - x[0]) / x[2]) * len(self._constRanges['fields'])
            
        return r
    
    def get_results(self, num=None):
        if num:
            num = min(len(self.heap), num)
        else:
            num = min(len(self.heap), self.num_results)
            
        return heapq.nlargest(num, self.heap)
    
    
    def _xrange(self, x, y, step):
        while x < y:
            yield float(x)
            x += step
            
    def _score(self, scorer):
        hits = [0.0] * len(self.docs)
        i= 0
        for d in self.docs:
            hits[i] = (scorer.run(d['formula'], docid=d['docid']), d['docid'])
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
        
    def _get_const_ranges(self):
        if not self.constRanges:
            yield {}
        else:
            if self._constRanges:
                fields = self._constRanges['fields']
                range = self._constRanges['range']
            else:
                fields = self.constRanges['fields']
                range = self.constRanges['range']
            
            range = list(self._xrange(*range))
            for x in itertools.combinations(range, len(fields)):
                yield dict(zip(fields, x))

    def _optimize_constant_search_space(self):
        """Find what fields, if any are used by the const()
        in any of the docs and then use only those fields
        for const() execution.
        """
        if not self.constRanges:
            return
        
        range = self.constRanges['range']
        fields = self._find_const_fields()
        
        if not fields:
            self._constRanges = {'fields': [], 'range': range}
        else:
            self._constRanges = {'fields': fields, 'range': range}
        
    def _find_const_fields(self):
        
        class ConstCollector(FlexibleScorer):
            def __init__(self, *args, **kwargs):
                FlexibleScorer.__init__(self, *args, **kwargs)
                self.const_fields = set()        
            def const(self, query, boost, querynorm):
                field, the_rest = query.split(':', 1)
                self.const_fields.add(field)
                return querynorm * boost
        scorer = ConstCollector()
        for d in self.docs:
            scorer.run(d['formula'])
        return list(scorer.const_fields)
            
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