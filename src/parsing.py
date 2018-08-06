from lark import Lark

grammar=r"""
    expr: (FLOAT EQUAL operation expr)+
        | qweight
    
    qweight: (FLOAT EQUAL item operation?)+
        
    
    item: weight  
        | score
        | idf
        | tfnorm
        | boost
        
    
    operation: "result of:" -> resultof
              | "sum of:" -> sum
              | "max of:" -> maxof
              | "computed from:" -> computedfrom 
              | "product of:" -> product

    
    weight: "weight" "(" DESCRIPTION+ ")" "[SchemaSimilarity]" COMMA
    
    score: "score" "(" (DESCRIPTION | EQUAL | COMMA)+ ")" COMMA
    
    boost: "boost" 
    
    idf: ("idf" "(" idfdata ")")
        | ("idf(), sum of:" FLOAT EQUAL idf+)
        
    
    tfnorm: "tfNorm" COMMA operation tffreq tfk1 tfb tfavgdl tfdl
    tffreq:  FLOAT EQUAL ("termFreq"|"phraseFreq") EQUAL FLOAT
    tfk1: FLOAT EQUAL "parameter k1"
    tfb: FLOAT EQUAL "parameter b"
    tfavgdl: FLOAT EQUAL "avgFieldLength"
    tfdl: FLOAT EQUAL "fieldLength"
    
    idfdata: docfreq COMMA doccount
    
    docfreq: "docFreq" EQUAL DIGIT+
    
    doccount: "docCount" EQUAL nums
    
    nums: DIGIT+
    EQUAL: "="
    
    COMMA: ","
    
    DESCRIPTION: ("a".."z"|"A".."Z"|":"|FLOAT|DIGIT|EQUAL)+ | ESCAPED_STRING 

    %import common.ESCAPED_STRING
    %import common.STRING_INNER
    %import common.FLOAT
    %import common.DIGIT
    %import common.WS
    %ignore WS
"""

test = r"""
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
expl_parser = Lark(grammar, start='expr')
tree = expl_parser.parse(test)
#print tree.pretty()

test= r"""
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
"""
tree = expl_parser.parse(test)
#print tree.pretty()



test= r"""
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
tree = expl_parser.parse(test)
print tree.pretty()