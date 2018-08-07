import re
from lark import Lark, Tree
from lark.indenter import Indenter

grammar=r"""

    
    _expr: key sumof
    
        
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
              | "max of:" -> maxof
              | "sum of:" -> sumof
              
    operation: "sum of:" -> sumof
              | "max of:" -> maxof
              

    
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

test1 = r"""
19.06905 = weight(title:foo in 270585) [SchemaSimilarity], result of:
  19.06905 = score(doc=270585,freq=1.0 = termFreq=1.0
), product of:
    14.582924 = idf(docFreq=8, docCount=18310579)
    1.3076288 = tfNorm, computed from:
      1.0 = termFreq=1.0
      1.2 = parameter k1
      0.75 = parameter b
      16.734879 = avgFieldLength
      7.111111 = fieldLength

"""

test2= r"""
25.458822 = sum of:
  25.458822 = sum of:
    13.096327 = weight(title:bar in 1109) [SchemaSimilarity], result of:
      13.096327 = score(doc=1109,freq=8.0 = termFreq=8.0
), product of:
        7.314764 = idf(docFreq=12040, docCount=18088648)
        1.7903963 = tfNorm, computed from:
          8.0 = termFreq=8.0
          1.2 = parameter k1
          0.75 = parameter b
          16.729553 = avgFieldLength
          28.444445 = fieldLength
    12.362495 = weight(title:syn::bar in 1109) [SchemaSimilarity], result of:
      12.362495 = score(doc=1109,freq=8.0 = termFreq=8.0
), product of:
        6.904893 = idf(docFreq=18140, docCount=18088648)
        1.7903963 = tfNorm, computed from:
          8.0 = termFreq=8.0
          1.2 = parameter k1
          0.75 = parameter b
          16.729553 = avgFieldLength
          28.444445 = fieldLength
"""


test3= r"""
132.459 = sum of:
  48.40565 = sum of:
    17.719193 = sum of:
      9.254193 = weight(title:weak in 51038) [SchemaSimilarity], result of:
        9.254193 = score(doc=51038,freq=2.0 = termFreq=2.0
), product of:
          5.993038 = idf(docFreq=45639, docCount=18284546)
          1.5441573 = tfNorm, computed from:
            2.0 = termFreq=2.0
            1.2 = parameter k1
            0.75 = parameter b
            16.773111 = avgFieldLength
            10.24 = fieldLength
      8.464998 = weight(title:syn::weak in 51038) [SchemaSimilarity], result of:
        8.464998 = score(doc=51038,freq=2.0 = termFreq=2.0
), product of:
          5.4819536 = idf(docFreq=76085, docCount=18284546)
          1.5441573 = tfNorm, computed from:
            2.0 = termFreq=2.0
            1.2 = parameter k1
            0.75 = parameter b
            16.773111 = avgFieldLength
            10.24 = fieldLength
    30.686459 = max of:
      25.69286 = sum of:
        14.244011 = weight(abstract:lensing in 51038) [SchemaSimilarity], result of:
          14.244011 = score(doc=51038,freq=5.0 = termFreq=5.0
), product of:
            1.3 = boost
            6.076104 = idf(docFreq=27671, docCount=12046232)
            1.8032824 = tfNorm, computed from:
              5.0 = termFreq=5.0
              1.2 = parameter k1
              0.75 = parameter b
              184.32286 = avgFieldLength
              163.84 = fieldLength
        11.448849 = weight(abstract:syn::lens in 51038) [SchemaSimilarity], result of:
          11.448849 = score(doc=51038,freq=6.0 = termFreq=6.0
), product of:
            1.3 = boost
            4.736986 = idf(docFreq=105585, docCount=12046232)
            1.8591583 = tfNorm, computed from:
              6.0 = termFreq=6.0
              1.2 = parameter k1
              0.75 = parameter b
              184.32286 = avgFieldLength
              163.84 = fieldLength
      30.686459 = sum of:
        17.067314 = weight(title:lensing in 51038) [SchemaSimilarity], result of:
          17.067314 = score(doc=51038,freq=2.0 = termFreq=2.0
), product of:
            1.5 = boost
            7.3685555 = idf(docFreq=11533, docCount=18284546)
            1.5441573 = tfNorm, computed from:
              2.0 = termFreq=2.0
              1.2 = parameter k1
              0.75 = parameter b
              16.773111 = avgFieldLength
              10.24 = fieldLength
        13.619145 = weight(title:syn::lens in 51038) [SchemaSimilarity], result of:
          13.619145 = score(doc=51038,freq=2.0 = termFreq=2.0
), product of:
            1.5 = boost
            5.879861 = idf(docFreq=51108, docCount=18284546)
            1.5441573 = tfNorm, computed from:
              2.0 = termFreq=2.0
              1.2 = parameter k1
              0.75 = parameter b
              16.773111 = avgFieldLength
              10.24 = fieldLength
  84.053345 = sum of:
    44.864044 = weight(title:"(weak syn::weak) (lensing syn::lens)" in 51038) [SchemaSimilarity], result of:
      44.864044 = score(doc=51038,freq=4.0 = phraseFreq=4.0
), product of:
        24.723408 = idf(), sum of:
          5.993038 = idf(docFreq=45639, docCount=18284546)
          5.4819536 = idf(docFreq=76085, docCount=18284546)
          7.3685555 = idf(docFreq=11533, docCount=18284546)
          5.879861 = idf(docFreq=51108, docCount=18284546)
        1.8146384 = tfNorm, computed from:
          4.0 = phraseFreq=4.0
          1.2 = parameter k1
          0.75 = parameter b
          16.773111 = avgFieldLength
          10.24 = fieldLength
    12.878392 = weight(title:syn::weak lensing in 51038) [SchemaSimilarity], result of:
      12.878392 = score(doc=51038,freq=2.0 = termFreq=2.0
), product of:
        8.340078 = idf(docFreq=4365, docCount=18284546)
        1.5441573 = tfNorm, computed from:
          2.0 = termFreq=2.0
          1.2 = parameter k1
          0.75 = parameter b
          16.773111 = avgFieldLength
          10.24 = fieldLength
    13.092413 = weight(title:syn::gravitational microlensing in 51038) [SchemaSimilarity], result of:
      13.092413 = score(doc=51038,freq=2.0 = termFreq=2.0
), product of:
        8.478679 = idf(docFreq=3800, docCount=18284546)
        1.5441573 = tfNorm, computed from:
          2.0 = termFreq=2.0
          1.2 = parameter k1
          0.75 = parameter b
          16.773111 = avgFieldLength
          10.24 = fieldLength
    13.218502 = weight(title:syn::weak gravitational lensing in 51038) [SchemaSimilarity], result of:
      13.218502 = score(doc=51038,freq=2.0 = termFreq=2.0
), product of:
        8.560334 = idf(docFreq=3502, docCount=18284546)
        1.5441573 = tfNorm, computed from:
          2.0 = termFreq=2.0
          1.2 = parameter k1
          0.75 = parameter b
          16.773111 = avgFieldLength
          10.24 = fieldLength
"""


def parse_tree(tree):    
    out = []
    _parse_tree(tree, out)
    return out

def has_child(t, v):
    if isinstance(t, Tree):
        for c in t.children:
            if hasattr(c, 'data') and c.data == v:
                return v
    return None

def _parse_tree(t, out):
    if not isinstance(t, Tree):
        return
    if t.data == 'idf':
        # nested idf, made of multiple idf's - multi-token sitation
        if has_child(t, 'idf'):
            out.append('sum(')
            l = len(out)
            for x in t.children[1:]:
                if len(out) != l:
                    out.append(', ')
                _parse_tree(x, out)
            out.append(')')
        else:
            out.append('idf(')
            out.append(t.children[1].children[0].value) # docfreq
            out.append(',')
            out.append(t.children[2].children[0].value) # doccount
            out.append(')')
    elif t.data == 'tfnorm':
        out.append('tf(')
        out.append(t.children[2].children[0].value) #tffreq
        out.append(',')
        out.append(t.children[3].children[0].value) #k1
        out.append(',')
        out.append(t.children[4].children[0].value) #b
        out.append(',')
        out.append(t.children[5].children[0].value) #avgdl
        out.append(',')
        out.append(t.children[6].children[0].value) #doclen
        out.append(')')
    
    elif t.data == 'expr' and isinstance(t.children[0], Tree):
        out.append('sum(')
        l=len(out)
        for x in t.children:
            if len(out) != l:
                out.append(', ')
                l=len(out)
            _parse_tree(x, out)
        out.append(')')
    elif t.data == 'expr' and not isinstance(t.children[0], Tree):
        if t.children[1].data == 'sumof':
            out.append('sum(')
        elif t.children[1].data == 'maxof':
            out.append('max(')
        else:
            raise Exception('Unknown tree: %s' % t)
        l=len(out)
        for x in t.children:
            if len(out) != l:
                out.append(', ')
                l=len(out)
            _parse_tree(x, out)
        out.append(')')
    elif has_child(t, 'productof'):
        out.append('product(')
        l = len(out)
        for x in t.children[1:]:
            if len(out) != l:
                out.append(', ')
                l = len(out)
            _parse_tree(x, out)
        out.append(')')
    else:
        for x in t.children:
            _parse_tree(x, out)

class TreeIndenter(Indenter):
    NL_type = '_NL'
    OPEN_PAREN_types = []
    CLOSE_PAREN_types = []
    INDENT_type = '_INDENT'
    DEDENT_type = '_DEDENT'
    tab_len = 2

def cleanup(text):
    t = re.sub(r'\n\)', ")", text, flags=re.MULTILINE)
    
    t2 = add_brackets(t)
    return t2

def add_brackets(t):
    """Because blocks are indented by space only, the parser makes
    mistakes in assigning children to proper parents. We add brackets
    to demarkate every block.
    """
    
    t = t.strip()
    lines = t.splitlines()
    i = 0
    
    while i < len(lines):
        if lines[i].endswith('sum of:') or lines[i].endswith('max of:'):
            _add_brackets(i, lines)
        i += 1
    return '\n'.join(lines)
    
def _add_brackets(i, lines):
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


expl_parser = Lark(grammar, start='_expr')
tree = expl_parser.parse(cleanup(test2))
print tree.pretty(indent_str='   ')

print ''.join(parse_tree(tree))