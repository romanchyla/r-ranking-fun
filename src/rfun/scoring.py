import re
from lark import Lark, Tree, Transformer, Visitor
from lark.tree import pydot__tree_to_png
import math

# #| ("sum of:" "[" (key weight)+ "]") -> sumof

grammar=r"""

    
    start: (key sumof) | (key weight)
    
        
    sumof: ( "sum of:" "[" (key (weight | sumof))+ "]" ) -> sumof
        | ( "max of:" "[" (key (weight | sumof))+ "]" ) -> maxof
        
    
    key: FLOAT _EQUAL -> result
        
    weights: "sum of:" weight+
    weight: ("weight" "(" wdescription ")" "[SchemaSimilarity]" _COMMA wscore) -> weight
        | (const _COMMA woperation boost querynorm) -> constant
        
    
    maxweight: "max of:" ((key weights)|weight)+
    
 
    wdescription: DESCRIPTION+ -> wdescription
    qterm: ("a".."z"|"A".."Z"|":"|FLOAT|DIGIT | ESCAPED_STRING|":"|","|"*"|"?")+
    
    wscore: woperation score
        
    woperation:"result of:" -> resultof
              | "product of:" -> productof
              | "computed from:" -> computedfrom

    score: FLOAT _EQUAL scoredesc _COMMA scorecomp
    scoredesc: "score" "(" (DESCRIPTION | _EQUAL | _COMMA)+ ")"
    scorecomp:  woperation boost? idf tfnorm
    
    boost: FLOAT _EQUAL "boost"
    
    idf: FLOAT _EQUAL (("idf" "(" _idfdata ")") | ("idf(), sum of:" "[" idf+ "]" ))
    tfnorm: FLOAT _EQUAL "tfNorm" _COMMA woperation tfreq tfk1 tfb tfavgdoclen? tfdl?
        
    
    tfreq:  FLOAT _EQUAL (("termFreq"|"phraseFreq") _EQUAL _FLOAT)
    tfk1: FLOAT _EQUAL "parameter k1"
    tfb: FLOAT _EQUAL "parameter b" ("(" anyterm+ ")")?
    tfavgdoclen: FLOAT _EQUAL "avgFieldLength"
    tfdl: FLOAT _EQUAL "fieldLength"
    
    _idfdata: docfreq _COMMA doccount
    docfreq: "docFreq" _EQUAL _nums
    
    
    doccount: "docCount" _EQUAL _nums
    querynorm: FLOAT _EQUAL "queryNorm"
    
    const: ("const(ConstantScore(" anyterm "))") 
        | ("const(" anyterm ")")
    
    anyterm: /[^)^\]]+/
    _nums: /\d+/
    EQUAL: "="
    _EQUAL: "="
    _FLOAT: FLOAT
    
    _COMMA: ","
    
    DESCRIPTION: ("a".."z"|"A".."Z"|":"|FLOAT|DIGIT)+ | ESCAPED_STRING
    

    %import common.ESCAPED_STRING
    %import common.STRING_INNER
    %import common.FLOAT
    %import common.DIGIT
    %import common.WS
    
    %ignore WS
    
"""


class ExplanationParser(object):
    def __init__(self, flatten_tfidf=False, use_kwargs=False):
        self.parser = Lark(grammar, parser='lalr')
        self.flatten_tfidf = flatten_tfidf
        self.use_kwargs = use_kwargs
        
    def parse(self, input):
        """Receives explanation from one lucene document (as generated
        by debugQuery=true with json output), will parse it into an AST
        and extract final score together with the algebraic expression
        that summarizes the whole scoring chain
        """
        
        # XXX: in true OOM fashion we should save tree with the instance
        # however I am using this class only as a wrapper for useful
        # methods; maybe will change that later...
        tree = self._get_tree(input)
        visitor = TreeVisitor(flatten_tfidf=self.flatten_tfidf,
                              use_kwargs=self.use_kwargs) 
        visitor.visit(tree)
        return (float(visitor.score), visitor.formula)
    
    def _get_tree(self, input):        
        return self.parser.parse(self._cleanup(input))
        
    def get_tree(self, input, destination=None):
        """Generates readable representation of the input
        optionally can save graph into a PNG file"""
        
        tree = self._get_tree(input)
        out = tree.pretty(indent_str=' ')
        
        if destination:
            pydot__tree_to_png(tree, destination)
        
        return out

        
    def _cleanup(self, text):
        t = re.sub(r'\n\s*\)', ")", text, flags=re.MULTILINE)
        t2 = self._check_constant(self._add_brackets(t))
        
        #print t2
        return t2

    def _add_brackets(self, t):
        """Because blocks are indented by space only, the parser makes
        mistakes in assigning children to proper parents. We add brackets
        to demarkate every block.
        """
        
        t = t.strip()
        lines = t.splitlines()
        i = 0
        
        while i < len(lines):
            if lines[i].endswith('sum of:') or lines[i].endswith('max of:'):
                self.__add_brackets(i, lines)
            i += 1
        return '\n'.join(lines)
        
    def __add_brackets(self, i, lines):
        assert i < len(lines)
        
        def count_indent(line):
            j = 0
            while j < len(line):
                if line[j] != " ":
                    break
                j += 1
            return j
        
        # count number of spaces in the starting line
        indent = count_indent(lines[i])
        
        
        # now go through all bottom lines and consider all children
        # (only those that have higher indent)
        j = i
        while j+1 < len(lines):
            k = count_indent(lines[j+1])
            if k > indent:
                j+=1
            else:
                break
    
        # i points to the start of the block, j = end of block
        lines[i] += '['
        lines[j] += ']'

 
    def _check_constant(self, text):
        """Some query types are missing const(qterm) and have just "qterm, product of:"
        """
        lines = text.splitlines()
        for i in range(len(lines)):
            line = lines[i]
            if line.endswith('product of:') or line.endswith('computed from:') or line.endswith('result of:'):
                parts = line.split(' = ')
                t = parts[1]
                if t.startswith('weight') or t.startswith('score') or t.startswith('const'):
                    continue
                if i-1 > 0 and not lines[i-1].endswith('['):
                    continue
                lines[i] = self._add_constant(line)
        return '\n'.join(lines)
    
    def _add_constant(self, line):
        i = line.index(' = ') + 3
        j = 0
        for x in (', product of:', ', result of:', ', computed from:'):
            if x in line:
                j = line.index(x)
                break
        return line[0:i] + 'const(' + line[i:j] + ')' + line[j:]




class TreeVisitor(Visitor):
    """Will extract algebraic expression from the parsed tree"""
    def __init__(self, use_kwargs=False, flatten_tfidf=False):
        self.use_kwargs = use_kwargs
        self.flatten_tfidf = flatten_tfidf
        
        # default templates
        tmpl = {}
        tmpl['idf'] = 'idf(%s, %s)'
        tmpl['idfgroup'] = 'idfgroup(%s)'
        tmpl['tfnorm'] = 'tf(%s, %s, %s, %s, %s)'
        tmpl['sumof'] = 'sum(%s)'
        tmpl['maxof'] = 'max(%s)'
        tmpl['weight'] = 'weight("%s", %s, %s)'
        tmpl['const'] = 'const(%s, %s)'
        
        # over-rides
        if self.use_kwargs and self.flatten_tfidf:
            tmpl['idf'] = 'tfreq=%s, k1=%s, b=%s, avgdoclen=%s, doclen=%s'
            tmpl['idfgroup'] = 'docfreq=None, colfreq=None, idfgroup=(dict(%s))'
            
        elif self.use_kwargs and not self.flatten_tfidf:
            tmpl['idf'] = 'tf(tfreq=%s, k1=%s, b=%s, avgdoclen=%s, doclen=%s)'
            tmpl['idfgroup'] = 'docfreq=None, colfreq=None, idfgroup=(%s)'
            
        elif not self.use_kwargs and self.flatten_tfidf:
            tmpl['idf'] = '%s, %s, %s, %s, %s'
            tmpl['idfgroup'] = 'idfgroup=((%s))'
        
        
    def idf(self, node):
        # for phrases, idf for every token
        out = []
        for x in node.children: # nested idf()
            if hasattr(x, 'formula'):
                out.append(x.formula)
        if len(out): 
            if self.use_kwargs:
                if self.flatten_tfidf:
                    node.formula = 'docfreq=None, colfreq=None, idfgroup=(dict(%s))' % ('), dict('.join(out))
                else:
                    node.formula = 'docfreq=None, colfreq=None, idfgroup=(%s)' % (', '.join(out))
            else:
                if self.flatten_tfidf:
                    node.formula = 'idfgroup=((%s))' % ('), ('.join(out))
                else:
                    node.formula = 'idfgroup(%s)' % (', '.join(out))
        else:
            if self.use_kwargs:
                if self.flatten_tfidf:
                    node.formula = 'docfreq=%s, colfreq=%s' % (node.children[1].children[0].value, node.children[2].children[0].value)
                else:
                    node.formula = 'idf(docfreq=%s, colfreq=%s)' % (node.children[1].children[0].value, node.children[2].children[0].value)
            else: 
                if self.flatten_tfidf:
                    node.formula = '%s, %s' % (node.children[1].children[0].value, node.children[2].children[0].value)
                else:
                    node.formula = 'idf(%s, %s)' % (node.children[1].children[0].value, node.children[2].children[0].value)
            
    def tfnorm(self, node):
        if self.use_kwargs and self.flatten_tfidf:
            tmpl = 'tfreq=%s, k1=%s, b=%s, avgdoclen=%s, doclen=%s'
        elif self.use_kwargs and not self.flatten_tfidf:
            tmpl = 'tf(tfreq=%s, k1=%s, b=%s, avgdoclen=%s, doclen=%s)'
        elif not self.use_kwargs and self.flatten_tfidf:
            tmpl = '%s, %s, %s, %s, %s'
        else:
            tmpl = 'tf(%s, %s, %s, %s, %s)'
            
        node.formula = tmpl % (
            node.children[2].children[0].value, #tfreq
            node.children[3].children[0].value, #k1
            node.children[4].children[0].value, #b
            len(node.children) >= 6 and node.children[5].children[0].value or '0', #avgdoclen
            len(node.children) >= 7 and node.children[6].children[0].value or '0') #doclen
    
    def boost(self, node):
        node.formula = node.children[0].value 
        
    def sumof(self, node):
        out = []
        for x in node.children:
            if hasattr(x, 'formula'):
                out.append(x.formula)
        node.formula = 'sum(%s)' % ', '.join(out)
        
    def maxof(self, node):
        out = []
        for x in node.children:
            if hasattr(x, 'formula'):
                out.append(x.formula)
        node.formula = 'max(%s)' % ', '.join(out)
        
    def wdescription(self, node):
        out = []
        for x in node.children:
            out.append(str(x).replace('"', '\\"'))
        node.formula = (' '.join(out))
        
    def weight(self, node):
        idf = self._find(node, 'idf')
        tf = self._find(node, 'tfnorm')
        descr = self._find(node, 'wdescription')
        boost = self._find(node, 'boost')
        
        if boost:
            if self.use_kwargs:
                if self.flatten_tfidf:
                    node.formula = 'weight(term="%s", %s, %s, boost=%s)' % (descr, tf, idf, boost)
                else:
                    node.formula = 'weight(term="%s", tf=%s, idf=%s, boost=%s)' % (descr, tf, idf, boost)
            else:
                node.formula = 'weight("%s", %s, %s, %s)' % (descr, tf, idf, boost)
        else:
            if self.use_kwargs:
                if self.flatten_tfidf:
                    node.formula = 'weight(term="%s", %s, %s)' % (descr, tf, idf)
                else:
                    node.formula = 'weight(term="%s", tf=%s, idf=%s)' % (descr, tf, idf)
            else:
                node.formula = 'weight("%s", %s, %s)' % (descr, tf, idf)
        
    def _find(self, node, name):
        queue = [node]
        while len(queue):
            x = queue.pop()
            if isinstance(x, Tree):
                if x.data == name:
                    if hasattr(x, 'formula'):
                        return x.formula
                    else:
                        return x
                for c in x.children:
                    queue.insert(0, c)
    def start(self, node):
        for x in node.children:
            if hasattr(x, 'formula'):
                self.formula = x.formula
        self.score = node.children[0].children[0].value

    
    def querynorm(self, node):
        node.formula = node.children[0].value
        
    def constant(self, node):
        b = self._find(node, 'boost')
        qn = self._find(node, 'querynorm')
        anyterm = self._find(node, 'anyterm')
        query = []
        for child in anyterm.children:
            query.append(child.value)
        query = repr(' '.join(query))
        
        if self.use_kwargs:
            node.formula = 'const(query=%s, boost=%s, querynorm=%s)' % (query, b, qn)
        else:
            node.formula = 'const(%s, %s, %s)' % (query, b, qn)
            

class LuceneBM25Scorer(object):
    """Should produce exactly the same results as Lucene"""
    
    def idfgroup(self, *args):
        return sum(args)
    
    def sum(self, *args):
        return sum(args)
    
    def weight(self, term, tf, idf, boost=None):
        if boost is not None:
            return tf * idf * boost
        return tf * idf
    
    def max(self, *args):
        return max(args)
    
    def tf(self, tfreq, k1, b, avgdoclen, doclen):
        if avgdoclen == 0: # probably a constant score, just return freq
            return tfreq
        L = doclen/avgdoclen
        return ((k1+1)*tfreq)/(k1*(1.0-b+b*L)+tfreq)
    
    def idf(self, docfreq, colfreq):
        return math.log(1+(colfreq-docfreq+0.5)/(docfreq + 0.5))
    
    def const(self, query, boost, querynorm):
        return querynorm * boost
    
    def run(self, formula):
        return self._eval(formula)
    
    def _eval(self, formula):
        """Executes the calculation and returns the final score"""
        locals = {
            'sum': self.sum,
            'max': self.max,
            'weight': self.weight,
            'tf': self.tf,
            'idf': self.idf,
            'idfgroup': self.idfgroup,
            'const': self.const,
            }
        return eval(formula, None, locals)

    

class FlexibleScorer(LuceneBM25Scorer):
    """With this class we can vary parameters that are used
    for computation of the scores. The algebraic formulas
    consumed by this scorer have to be generated with
    flatten_tfidf=True; so they have to look like so:
    
    weight("title:foo", 1.0, 1.2, 0.75, 16.734879, 7.111111, 8, 18310579)
        or 
    weight(term="title:foo in 12019", tfreq=1.0, k1=1.2, b=0.75, avgdoclen=16.734879, doclen=7.111111, docfreq=8, colfreq=18310579)
    """
    
    def __init__(self, k1=1.2, b=0.75, perfield_kb=None,
                 idf_normalization=False, perfield_avgdoclen=None,
                 perdoc_boost=None, consts=None):
        """
        Parameters and how they affect score calculations:
        
            @param k1 : k1 to override defaults (used if perfield_kb[field] is not found)
            @param b : to override b on BM25 computation (in the k1*(1-b+b*L))
            @param perfield_kb: dict, contains k1 and b values specific to a field, 
                example: {'title_k1': 1.2, 'body_b': 0.5}
            @param idf_normalization: bool, whether to normalize IDF portion of the
                formula before calculating the final score; see 
                normalize_idf method for details. NOTE: normalizatin will double 
                the time we spend in performing the calculations.
            @param perfield_avgdoclen: dict, to override average doclen that is
                used for computation in |doclen|/avgDocLen -- which is the L
                factor of BM25 formula (a part of length normalization); you may 
                want to use median instead of averages for example
            @param perdoc_boost: dict, this is a boost applied to every weight
                calculation (see description in the get_boost()) -- you may want to
                pass any numerical (float) value in here; for example values from
                inside 'classic_factor' field
            @param consts: dict, a boost that should be applied (per field) during
                const() evaluation
        
        """
        self.k1 = float(k1)
        self.b = float(b)
        self.perfield_kb = perfield_kb or {}
        self.perfield_avgdoclen = perfield_avgdoclen or {}
        self.perdoc_boost = perdoc_boost or {}
        self.idf_normalization = bool(idf_normalization)
        self.consts = consts or {}
        
        for k,v in self.perdoc_boost.items():
            if not isinstance(k, basestring) or not isinstance(v, float):
                raise Exception('docboost keys (docids) must be strings and values must be floats')
            
        self.idf_normalization_factor = None
        if idf_normalization:
            # instantiate a new class (with exactly the same params as we have)
            # it will be used to calculate the magniture of the weight factor
            self.normalizer = IDFNormalizer(k1=self.k1, b=self.b, perfield_kb=self.perfield_kb,
                 idf_normalization=True, perfield_avgdoclen=self.perfield_avgdoclen,
                 perdoc_boost=self.perdoc_boost)

    
    def get_boost(self, field, docid, default_boost):
        """Remember, the boost is for every weight object; if we were
        to apply boost only to the final result (using classic_factor)
        or some such thing, we'll have to modify lucene scoring/search
        mechanism. But maybe the field boost is a close approximation;
        in the end it is applied to every weight (well, maybe not the 
        constant score)"""
        
        return self.perdoc_boost.get(docid, default_boost)
        
    def weight(self, term, tfreq, k1, b, avgdoclen, doclen, docfreq, colfreq, 
               boost=None, idfgroup=None):
        
        # override k1/b factors specific to a field (or use defaults)
        field = term.split(':')[0]
        docid = term.split(' ')[-1]
        
        k1 = self.perfield_kb.get('%s_k1' % field, self.k1)
        b = self.perfield_kb.get('%s_b' % field, self.b)
        
        # compute idf
        if idfgroup:
            idf = 0
            for x in idfgroup:
                if isinstance(x, dict):
                    idf += self.idf(**x)
                elif isinstance(x, float):
                    idf += x
                else:
                    idf += self.idf(*x) 
        else:
            idf = self.idf(docfreq, colfreq)
            
        
        # normalize the IDF (lucene can do this)
        if self.idf_normalization:
            idf = self.normalize_idf(idf, k1, b, avgdoclen, doclen)
        
        
        # compute tf
        avgdoclen = self.perfield_avgdoclen.get(field, avgdoclen)
        tf = self.tf(tfreq, k1, b, avgdoclen, doclen)
        
        boost = self.get_boost(field, docid, boost)
        
        if boost:
            return tf * idf * boost
        else:
            return tf * idf
        
    def normalize_idf(self, idf, k1, b, avgdoclen, doclen):
        """Lucene does normalization for TF*IDF, it doesn't have
        this functionality for BM25 Similarity classes; it does so by
        summing all weights from the scorers; the weight in the lucene's world 
        is IDF * norm which translates to: 
            IDF * k1 * (1-b+b*L) 
            where L is avgdoclen/docLen
        """
        
        if self.idf_normalization_factor is not None:
            return idf / self.idf_normalization_factor
        else:
            return idf
        
    def run(self, formula):
        if self.idf_normalization:
            self.idf_normalization_factor = self.normalizer.run(formula)
        else:
            self.idf_normalization_factor = None
        
        return self._eval(formula)
    
    def const(self, query, boost, querynorm):
        field, rest = query.split(':', 1)
        boost = self.consts.get(field, boost)
        return querynorm * boost
        
        
class IDFNormalizer(FlexibleScorer):        
    """Purpose of this class is to extract the weight magnitude
    from the relevancy score; we do it by setting TF and boost
    parts to 1.0"""
    def __init__(self, *args, **kwargs):
        kwargs['idf_normalization'] = False
        FlexibleScorer.__init__(self, *args, **kwargs)
        self.idf_normalization = True
        
    def tf(self, tfreq, k1, b, avgdoclen, doclen):
        return 1.0
    def get_boost(self, field, docid, default_boost):
        return 1.0
    def normalize_idf(self, idf, k1, b, avgdoclen, doclen):
        if doclen == 0:
            return idf
        return idf * k1 * (1.0-b+b*(avgdoclen/doclen))
    def run(self, formula):
        return self._eval(formula)