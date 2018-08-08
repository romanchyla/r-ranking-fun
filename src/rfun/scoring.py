import re
from lark import Lark, Tree, Transformer, Visitor
from lark.tree import pydot__tree_to_png
import math

class ExplanationParser(object):
    def __init__(self):
        self.parser = Lark(grammar)
        
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
        visitor = TreeVisitor() 
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
        t = re.sub(r'\n\)', ")", text, flags=re.MULTILINE)
        t2 = self._add_brackets(t)
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

 

grammar=r"""

    
    start: key (sumof | weight)
    
        
    sumof: ("sum of:" "[" (key weight)+ "]") -> sumof
        | ("sum of:" "[" (key sumof)+ "]") -> sumof
        | ("max of:" "[" (key sumof)+ "]" ) -> maxof
        
    
    key: FLOAT _EQUAL -> result
        
    weights: "sum of:" weight+
    weight: "weight" "(" wdescription ")" "[SchemaSimilarity]" _COMMA wscore
    maxweight: "max of:" ((key weights)|weight)+
    
 
    wdescription: DESCRIPTION+ -> wdescription
    wscore: woperation score
        
    woperation:"result of:" -> resultof
              | "product of:" -> productof
              | "computed from:" -> computedfrom

    score: FLOAT _EQUAL scoredesc _COMMA scorecomp
    scoredesc: "score" "(" (DESCRIPTION | _EQUAL | _COMMA)+ ")"
    scorecomp:  woperation boost? idf tfnorm
    
    boost: FLOAT _EQUAL "boost" 
    
    idf: FLOAT _EQUAL (("idf" "(" _idfdata ")") | ("idf(), sum of:" "[" idf+ "]" ))
        
    
    tfnorm: FLOAT _EQUAL "tfNorm" _COMMA woperation tffreq tfk1 tfb tfavgdl tfdl
    tffreq:  FLOAT _EQUAL (("termFreq"|"phraseFreq") _EQUAL _FLOAT)
    tfk1: FLOAT _EQUAL "parameter k1"
    tfb: FLOAT _EQUAL "parameter b"
    tfavgdl: FLOAT _EQUAL "avgFieldLength"
    tfdl: FLOAT _EQUAL "fieldLength"
    
    _idfdata: docfreq _COMMA doccount
    
    docfreq: "docFreq" _EQUAL _nums
    
    doccount: "docCount" _EQUAL _nums
    
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




class TreeVisitor(Visitor):
    """Will extract algebraic expression from the parsed tree"""    
    def idf(self, node):
        # for phrases, idf for every token
        out = []
        for x in node.children:
            if hasattr(x, 'formula'):
                out.append(x.formula)
        if len(out):
            node.formula = 'idfgroup(%s)' % (', '.join(out))
        else:
            node.formula = 'idf(%s, %s)' % (node.children[1].children[0].value, node.children[2].children[0].value)
            
    def tfnorm(self, node):
        node.formula = 'tf(%s, %s, %s, %s, %s)' % (
            node.children[2].children[0].value, #tffreq
            node.children[3].children[0].value, #k1
            node.children[4].children[0].value, #b
            node.children[5].children[0].value, #avgdl
            node.children[6].children[0].value) #doclen
    
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
    def weight(self, node):
        idf = self._find(node, 'idf')
        tf = self._find(node, 'tfnorm')
        descr = self._find(node, 'wdescription')
        boost = self._find(node, 'boost')
        
        if boost:
            node.formula = 'weight("%s", %s, %s, %s)' % (descr.children[0].value, tf, idf, boost)
        else:
            node.formula = 'weight("%s", %s, %s)' % (descr.children[0].value, tf, idf)
        
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



class Scorer():
    """Base class for scoring lucene documents"""
    
    parser = ExplanationParser()
    
    def __init__(self, input):
        score, formula = Scorer.parser.parse(input)
        self.orig_score = score
        self.formula = formula
        
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
    
    def tf(self, freq, k1, b, avgdoclen, doclen):
        L = doclen/avgdoclen
        return ((k1+1)*freq)/(k1*(1.0-b+b*L)+freq)
    
    def idf(self, docfreq, doccount):
        return math.log(1+(doccount-docfreq+0.5)/(docfreq + 0.5))
    
    def run(self):
        """Executes the calculation and returns the final score"""
        locals = {
            'sum': self.sum,
            'max': self.max,
            'weight': self.weight,
            'tf': self.tf,
            'idf': self.idf,
            'idfgroup': self.idfgroup}
        return eval(self.formula, None, locals)