# --encoding: utf8 --
import unittest
import timeit
import sys

from rfun.scoring import ExplanationParser, Scorer

class Test(unittest.TestCase):
    
    def test_pure_weight(self):
        p = ExplanationParser()
        score, formula = p.parse(test1)
        self.assertEquals(score, 19.06905)
        self.assertEquals(formula, 'weight("title:foo", tf(1.0, 1.2, 0.75, 16.734879, 7.111111), idf(8, 18310579))')
        
    def test_simple(self):
        p = ExplanationParser()
        score, formula = p.parse(test2)
        self.assertEquals(score, 25.458822)
        self.assertEquals(formula, 'sum(sum(weight("title:bar", tf(8.0, 1.2, 0.75, 16.729553, 28.444445), idf(12040, 18088648)), weight("title:syn::bar", tf(8.0, 1.2, 0.75, 16.729553, 28.444445), idf(18140, 18088648))))')

    def test_complex(self):
        self.maxDiff = None
        p = ExplanationParser()
        score, formula = p.parse(test3)
        self.assertEquals(score, 132.459)
        self.assertEquals(formula, 'sum(sum(sum(weight("title:weak", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(45639, 18284546)), weight("title:syn::weak", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(76085, 18284546))), max(sum(weight("abstract:lensing", tf(5.0, 1.2, 0.75, 184.32286, 163.84), idf(27671, 12046232), 1.3), weight("abstract:syn::lens", tf(6.0, 1.2, 0.75, 184.32286, 163.84), idf(105585, 12046232), 1.3)), sum(weight("title:lensing", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(11533, 18284546), 1.5), weight("title:syn::lens", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(51108, 18284546), 1.5)))), sum(weight("title:", tf(4.0, 1.2, 0.75, 16.773111, 10.24), idfgroup(idf(45639, 18284546), idf(76085, 18284546), idf(11533, 18284546), idf(51108, 18284546))), weight("title:syn::weak", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(4365, 18284546)), weight("title:syn::gravitational", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(3800, 18284546)), weight("title:syn::weak", tf(2.0, 1.2, 0.75, 16.773111, 10.24), idf(3502, 18284546))))')
        
    def test_get_tree(self):
        self.maxDiff = None
        p = ExplanationParser()
        tree = p.get_tree(test1)
        tree = tree.replace('\t', '    ')
        self.assertEquals(tree, test1_tree)

    def test_scorer(self):
        for s,t in ((19.06905, test1), (25.458822, test2), (132.459, test3)):
            scorer = Scorer(t)
            self.assertAlmostEqual(s, scorer.run(), msg="Computed result %s differs too much from the one reported by Lucene (%s)" % (s, scorer.run()), delta=0.00005)


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
      tffreq    1.0
      tfk1    1.2
      tfb    0.75
      tfavgdl    16.734879
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


        

    


if __name__ == "__main__":
    unittest.main()