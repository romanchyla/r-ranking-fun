# --encoding: utf8 --
import unittest
import timeit
import sys
import math

from rfun.scoring import ExplanationParser, LuceneBM25Scorer, IDFNormalizer,\
    FlexibleScorer

class Test(unittest.TestCase):
    
    def test_pure_weight(self):
        p = ExplanationParser()
        score, formula = p.parse(test1)
        self.assertEquals(score, 19.06905)
        self.assertEquals(formula, 'weight("title:foo in 270585", tf(1.0, 1.2, 0.75, 16.734879, 7.111111), idf(8, 18310579))')
    
    def test_output_params(self):
        p = ExplanationParser(use_kwargs=True, flatten_tfidf=False)
        _, formula = p.parse(test1)
        self.assertEquals(formula, 'weight(term="title:foo in 270585", tf=tf(tfreq=1.0, k1=1.2, b=0.75, avgdoclen=16.734879, doclen=7.111111), idf=idf(docfreq=8, colfreq=18310579))')
        
        p = ExplanationParser(use_kwargs=True, flatten_tfidf=True)
        _, formula = p.parse(test1)
        self.assertEquals(formula, 'weight(term="title:foo in 270585", tfreq=1.0, k1=1.2, b=0.75, avgdoclen=16.734879, doclen=7.111111, docfreq=8, colfreq=18310579)')
        
        p = ExplanationParser(use_kwargs=False, flatten_tfidf=True)
        _, formula = p.parse(test1)
        self.assertEquals(formula, 'weight("title:foo in 270585", 1.0, 1.2, 0.75, 16.734879, 7.111111, 8, 18310579)')
        
        p = ExplanationParser(use_kwargs=None, flatten_tfidf=None) # default
        _, formula = p.parse(test1)
        self.assertEquals(formula, 'weight("title:foo in 270585", tf(1.0, 1.2, 0.75, 16.734879, 7.111111), idf(8, 18310579))')
        
    def test_simple(self):
        p = ExplanationParser()
        score, formula = p.parse(test2)
        self.assertEquals(score, 25.458822)
        self.assertEquals(formula, 'sum(sum(weight("title:bar in 1109", tf(8.0, 1.2, 0.75, 16.729553, 28.444445), idf(12040, 18088648)), weight("title:syn::bar in 1109", tf(8.0, 1.2, 0.75, 16.729553, 28.444445), idf(18140, 18088648))))')
        
        

    def test_complex(self):
        self.maxDiff = None
        p = ExplanationParser()
        score, formula = p.parse(test3)
        self.assertEquals(score, 132.459)
        self.assertEquals(formula, 'sum(sum(sum(weight("title:weak in 51038", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(45639, 18284546)), weight("title:syn::weak in 51038", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(76085, 18284546))), max(sum(weight("abstract:lensing in 51038", tf(5.0, 1.2, 0.75, 184.32286, 163.84), idf(27671, 12046232), 1.3), weight("abstract:syn::lens in 51038", tf(6.0, 1.2, 0.75, 184.32286, 163.84), idf(105585, 12046232), 1.3)), sum(weight("title:lensing in 51038", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(11533, 18284546), 1.5), weight("title:syn::lens in 51038", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(51108, 18284546), 1.5)))), sum(weight("title: \\"(weak syn::weak) (lensing syn::lens)\\" in 51038", tf(4.0, 1.2, 0.75, 16.773111, 10.24), idfgroup(idf(45639, 18284546), idf(76085, 18284546), idf(11533, 18284546), idf(51108, 18284546))), weight("title:syn::weak lensing in 51038", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(4365, 18284546)), weight("title:syn::gravitational microlensing in 51038", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(3800, 18284546)), weight("title:syn::weak gravitational lensing in 51038", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(3502, 18284546))))')
        
        score,formula = p.parse(test6)
        self.assertEquals(score, 9.4076)
        self.assertEquals(formula, 'sum(max(sum(const(\'author:kurtz,*\', 2.0, 1.0)), sum(const(\'first_author:kurtz,*\', 5.0, 1.0))), weight("year:1989 in 169291", tf(1.0, 1.2, 0.0, 0, 0), idf(212871, 17470857)))')
        
        
    def test_get_tree(self):
        self.maxDiff = None
        p = ExplanationParser()
        tree = p.get_tree(test1)
        tree = tree.replace('\t', '    ')
        self.assertEquals(tree, test1_tree)
        
    def test_cases(self):
        self.assert_formula(test8, '''sum(max(const('author:accomazzi, author:accomazzi,*', 6.0, 1.0)), max(const('author:kurtz, author:kurtz,*', 6.0, 1.0)))''')
        self.assert_formula(test9, '''sum(max(const('author:accomazzi, author:accomazzi,*', 6.0, 1.0)), max(const('author:kurtz, author:kurtz,*', 6.0, 1.0), sum(const('first_author:kurtz,*', 5.0, 1.0))))''')
        self.assert_formula(test10, '''sum(max(const('author:accomazzi, author:accomazzi,*', 6.0, 1.0)), max(const('abstract:kurtz', 1.3, 1.0), const('author:kurtz, author:kurtz,*', 6.0, 1.0)))''')
        
    def assert_formula(self, input, expected):
        p = ExplanationParser(use_kwargs=False, flatten_tfidf=False)
        _, formula = p.parse(input)
        self.assertEqual(formula, expected)


    
class TestScorers(unittest.TestCase):
    
    def test_scorers(self):
        for s,t in ((19.06905, test1), (25.458822, test2), (132.459, test3), (21.956947, test4),
                    (29.833654, test5), (9.4076, test6), (26, test7), (12.0, test8)):
            p = ExplanationParser()
            p2 = ExplanationParser(use_kwargs=True, flatten_tfidf=True)
            _, formula = p.parse(t)
            _, formula2 = p2.parse(t)
            scorer = LuceneBM25Scorer()
            fscorer = FlexibleScorer()
            self.assertAlmostEqual(s, scorer.run(formula), msg="Computed result %s differs too much from the one reported by Lucene (%s)" % (s, scorer.run(formula)), delta=0.00005)
            self.assertAlmostEqual(s, fscorer.run(formula2), msg="Computed result %s differs too much from the one reported by Lucene (%s)" % (s, fscorer.run(formula2)), delta=0.00005)

    def test_normalizer(self):
        """The test is engineered in a way that 
            IDF ~= 1.0
            therefore normalization of the whole sum() is 2.0
            which returns normalized IDF 1.0/2.0 = 0.5
            tfreq is 1.0 and b=0
            so the returned score is 0.5 per term
            i.e. 1.0 total
        """
        s = IDFNormalizer(k1=1.0, b=0)
        
        docfreq = 1.0
        colfreq = math.e * docfreq + 0.35914
        formula = 'sum(sum(weight(term="title:bar in 1109", tfreq=1.0, k1=1.2, b=0.75, avgdoclen=16.729553, doclen=28.444445, docfreq={docfreq}, colfreq={colfreq}), weight(term="title:syn::bar in 1109", tfreq=1.0, k1=1.2, b=0.75, avgdoclen=16.729553, doclen=28.444445, docfreq={docfreq}, colfreq={colfreq})))'.format(colfreq=colfreq, docfreq=docfreq)
        self.assertAlmostEqual(2.0, s.run(formula), delta=0.00005)
        
        scorer = FlexibleScorer(k1=1.0, b=0, idf_normalization=True)
        self.assertAlmostEqual(1.0, scorer.run(formula))
        
    
    def test_flexible_scorer(self):
        
        formula = 'sum(sum(weight(term="title:bar in 1109", tfreq=8.0, k1=1.2, b=0.75, avgdoclen=16.729553, doclen=28.444445, docfreq=12040, colfreq=18088648), weight(term="title:syn::bar in 1109", tfreq=8.0, k1=1.2, b=0.75, avgdoclen=16.729553, doclen=28.444445, docfreq=18140, colfreq=18088648)))'
        s = FlexibleScorer(k1=1.0, b=0.75)
        self.assertAlmostEqual(23.88556, s.run(formula), delta=0.00005)

        s = FlexibleScorer(k1=2.0, b=0)
        self.assertAlmostEqual(34.127176, s.run(formula), delta=0.00005)
        
        s = FlexibleScorer(k1=2.0, b=0.5)
        self.assertAlmostEqual(31.89380, s.run(formula), delta=0.00005)
        
        s = FlexibleScorer(k1=2.0, b=0.5, idf_normalization=True)
        self.assertAlmostEqual(1.41229, s.run(formula), delta=0.00005)
        
        s = FlexibleScorer(k1=2.0, b=0.5, idf_normalization=False,
                           perfield_kb={'title_k1': 1.0, 'title_b': 0.75})
        self.assertAlmostEqual(23.88556, s.run(formula), delta=0.00005)
        
        s = FlexibleScorer(k1=2.0, b=0.5, idf_normalization=False,
                           perfield_kb={'title_k1': 1.0, 'title_b': 0.75},
                           perfield_avgdoclen={'title': 9})
        self.assertAlmostEqual(21.42246, s.run(formula), delta=0.00005)
        
        s = FlexibleScorer(k1=1.0, b=0.75, perdoc_boost={'1109': 0.5})
        self.assertAlmostEqual(23.88556/2, s.run(formula), delta=0.00005)

        
        formula = 'const(\'author:kurtz,*\', 2.0, 1.0)'
        s = FlexibleScorer(consts={'author': 5.0})
        self.assertAlmostEqual(5.0, s.run(formula), delta=0.00005)
        s = FlexibleScorer(consts={'authorx': 5.0})
        self.assertAlmostEqual(2.0, s.run(formula), delta=0.00005)
        s = FlexibleScorer(consts={'authorx': 5.0}, perdoc_boost={'1': 5.0})
        self.assertAlmostEqual(10.0, s.run(formula, docid='1'), delta=0.00005)
        
        

    
        
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

test1_tree=u"""start
 result    19.06905
 weight
  wdescription
   title:foo
   in
   270585
  wscore
   resultof
   score
    19.06905
    scoredesc
     doc
     270585
     freq
     1.0
     termFreq
     1.0
    scorecomp
     productof
     idf
      14.582924
      docfreq    8
      doccount    18310579
     tfnorm
      1.3076288
      computedfrom
      tfreq    1.0
      tfk1    1.2
      tfb    0.75
      tfavgdoclen    16.734879
      tfdl    7.111111
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


test4 = """21.956947 = sum of:
       19.956947 = max of:
         19.956947 = weight(abstract:kurtz in 3338) [SchemaSimilarity], result of:
           19.956947 = score(doc=3338,freq=2.0 = termFreq=2.0
     ), product of:
             1.3 = boost
             9.452687 = idf(docFreq=882, docCount=11245132)
             1.6240354 = tfNorm, computed from:
               2.0 = termFreq=2.0
               1.2 = parameter k1
               0.75 = parameter b
               183.8078 = avgFieldLength
               83.591835 = fieldLength
         2.0 = sum of:
           2.0 = author:kurtz,*, product of:
             2.0 = boost
             1.0 = queryNorm
       2.0 = max of:
         2.0 = sum of:
           2.0 = author:accomazzi,*, product of:
             2.0 = boost
             1.0 = queryNorm
"""        

test5 ="""29.833654 = max of:
       23.447416 = weight(abstract:kurtz in 17454) [SchemaSimilarity], result of:
         23.447416 = score(doc=17454,freq=4.0 = termFreq=4.0
     ), product of:
           1.3 = boost
           9.451701 = idf(docFreq=915, docCount=11654131)
           1.9082781 = tfNorm, computed from:
             4.0 = termFreq=4.0
             1.2 = parameter k1
             0.75 = parameter b
             184.91911 = avgFieldLength
             64.0 = fieldLength
       29.833654 = weight(title:kurtz in 17454) [SchemaSimilarity], result of:
         29.833654 = score(doc=17454,freq=1.0 = termFreq=1.0
     ), product of:
           1.5 = boost
           13.718743 = idf(docFreq=19, docCount=17701456)
           1.4497758 = tfNorm, computed from:
             1.0 = termFreq=1.0
             1.2 = parameter k1
             0.75 = parameter b
             16.553545 = avgFieldLength
             4.0 = fieldLength"""

test6 = """9.4076 = sum of:
  5.0 = max of:
    2.0 = sum of:
      2.0 = const(author:kurtz,*), product of:
        2.0 = boost
        1.0 = queryNorm
    5.0 = sum of:
      5.0 = const(first_author:kurtz,*), product of:
        5.0 = boost
        1.0 = queryNorm
  4.407601 = weight(year:1989 in 169291) [SchemaSimilarity], result of:
    4.407601 = score(doc=169291,freq=1.0 = termFreq=1.0), product of:
      4.407601 = idf(docFreq=212871, docCount=17470857)
      1.0 = tfNorm, computed from:
        1.0 = termFreq=1.0
        1.2 = parameter k1
        0.0 = parameter b (parameter omitted from index)"""

test7 = '''26.0 = max of:
  26.0 = ConstantScore(abstract:accomazzi), product of:
    26.0 = boost
    1.0 = queryNorm'''

test8 = '''12.0 = sum of:
  6.0 = max of:
    6.0 = ConstantScore(author:accomazzi, author:accomazzi,*), product of:
      6.0 = boost
      1.0 = queryNorm
  6.0 = max of:
    6.0 = ConstantScore(author:kurtz, author:kurtz,*), product of:
      6.0 = boost
      1.0 = queryNorm'''
      
test9 = '''12.0 = sum of:
  6.0 = max of:
    6.0 = ConstantScore(author:accomazzi, author:accomazzi,*), product of:
      6.0 = boost
      1.0 = queryNorm
  6.0 = max of:
    6.0 = ConstantScore(author:kurtz, author:kurtz,*), product of:
      6.0 = boost
      1.0 = queryNorm
    5.0 = sum of:
      5.0 = first_author:kurtz,*, product of:
        5.0 = boost
        1.0 = queryNorm
'''
          
test10 =  '''12.0 = sum of:
       6.0 = max of:
         6.0 = ConstantScore(author:accomazzi, author:accomazzi,*), product of:
           6.0 = boost
           1.0 = queryNorm
       6.0 = max of:
         1.3 = ConstantScore(abstract:kurtz), product of:
           1.3 = boost
           1.0 = queryNorm
         6.0 = ConstantScore(author:kurtz, author:kurtz,*), product of:
           6.0 = boost
           1.0 = queryNorm'''
           
if __name__ == "__main__":
    if True:
        unittest.main()
    else:
        test_input = test10
        p = ExplanationParser(use_kwargs=False, flatten_tfidf=False)
        print p.get_tree(test_input)
        _, formula = p.parse(test_input)
        print formula