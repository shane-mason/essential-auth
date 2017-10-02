import unittest
from phrasemetrics import PhraseMetrics, Metrics

class TestPhraseMetrics(unittest.TestCase):

    def test_rules(self):
        results = PhraseMetrics.rules(PhraseMetrics.metrics("}R-!6GbD"))
        self.assertEqual(len(results), 0)

        results = PhraseMetrics.rules(PhraseMetrics.metrics("}R-!6GbD"), number=3, spacial=4)
        self.assertIn(PhraseMetrics.more_numbers, results)
        self.assertIn(PhraseMetrics.more_special, results)


        results = PhraseMetrics.rules(PhraseMetrics.metrics("password123"))
        self.assertIn(PhraseMetrics.not_mixed, results)
        self.assertIn(PhraseMetrics.more_special, results)
        self.assertIn(PhraseMetrics.sequence, results)
        self.assertIn(PhraseMetrics.too_common, results)

        results = PhraseMetrics.rules(PhraseMetrics.metrics("aaaBBB1!"))
        self.assertIn(PhraseMetrics.repeating, results)
        self.assertIn(PhraseMetrics.more_entropy, results)


class TestMetrics(unittest.TestCase):

    def test_case_mix(self):

        self.assertFalse(Metrics.case_mix("cfvu rovit nzmyz qwhtnh ey lauyfdiv"))
        self.assertTrue(Metrics.case_mix("L!U'[N(a#QCMJ9EH"))
        self.assertTrue(Metrics.case_mix("`%!)@:rN^4W'"))
        self.assertTrue(Metrics.case_mix("PGZs4@y2"))
        self.assertFalse(Metrics.case_mix("yjjmqkuevd"))
        self.assertFalse(Metrics.case_mix("CDMZXLVWTF"))
        self.assertFalse(Metrics.case_mix("9105609999"))
        self.assertFalse(Metrics.case_mix("[&:/>!</|<"))
        self.assertTrue(Metrics.case_mix("2uPI`Y"))
        self.assertTrue(Metrics.case_mix(".X3Tk0"))

    def test_upper_case(self):
        self.assertEqual(Metrics.upper_case("cfvu rovit nzmyz qwhtnh ey lauyfdiv"), 0)
        self.assertEqual(Metrics.upper_case("L!U'[N(a#QCMJ9EH"), 9)
        self.assertEqual(Metrics.upper_case("`%!)@:rN^4W'"), 2)
        self.assertEqual(Metrics.upper_case("PGZs4@y2"), 3)
        self.assertEqual(Metrics.upper_case("yjjmqkuevd"), 0)
        self.assertEqual(Metrics.upper_case("CDMZXLVWTF"), 10)
        self.assertEqual(Metrics.upper_case("9105609999"), 0)
        self.assertEqual(Metrics.upper_case("[&:/>!</|<"), 0)
        self.assertEqual(Metrics.upper_case("2uPI`Y"), 3)
        self.assertEqual(Metrics.upper_case(".X3Tk0"), 2)

    def test_upper_case(self):
        self.assertEqual(Metrics.lower_case("cfvu rovit nzmyz qwhtnh ey lauyfdiv"), 30)
        self.assertEqual(Metrics.lower_case("L!U'[N(a#QCMJ9EH"), 1)
        self.assertEqual(Metrics.lower_case("`%!)@:rN^4W'"), 1)
        self.assertEqual(Metrics.lower_case("PGZs4@y2"), 2)
        self.assertEqual(Metrics.lower_case("yjjmqkuevd"), 10)
        self.assertEqual(Metrics.lower_case("CDMZXLVWTF"), 0)
        self.assertEqual(Metrics.lower_case("9105609999"), 0)
        self.assertEqual(Metrics.lower_case("[&:/>!</|<"), 0)
        self.assertEqual(Metrics.lower_case("2uPI`Y"), 1)
        self.assertEqual(Metrics.lower_case(".X3Tk0"), 1)


    def test_number(self):
        self.assertEqual(Metrics.number("cfvu rovit nzmyz qwhtnh ey lauyfdiv"), 0)
        self.assertEqual(Metrics.number("L!U'[N(a#QCMJ9EH"), 1)
        self.assertEqual(Metrics.number("`%!)@:rN^4W'"), 1)
        self.assertEqual(Metrics.number("PGZs4@y2"), 2)
        self.assertEqual(Metrics.number("yjjmqkuevd"), 0)
        self.assertEqual(Metrics.number("CDMZXLVWTF"), 0)
        self.assertEqual(Metrics.number("9105609999"), 10)
        self.assertEqual(Metrics.number("[&:/>!</|<"), 0)
        self.assertEqual(Metrics.number("2uPI`Y"), 1)
        self.assertEqual(Metrics.number(".X3Tk0"), 2)

    def test_special(self):
        self.assertEqual(Metrics.special("cfvu rovit nzmyz qwhtnh ey lauyfdiv"), 0)
        self.assertEqual(Metrics.special("L!U'[N(a#QCMJ9EH"), 5)
        self.assertEqual(Metrics.special("`%!)@:rN^4W'"), 8)
        self.assertEqual(Metrics.special("PGZs4@y2"), 1)
        self.assertEqual(Metrics.special("yjjmqkuevd"), 0)
        self.assertEqual(Metrics.special("CDMZXLVWTF"), 0)
        self.assertEqual(Metrics.special("9105609999"), 0)
        self.assertEqual(Metrics.special("[&:/>!</|<"), 10)
        self.assertEqual(Metrics.special("2uPI`Y"), 1)
        self.assertEqual(Metrics.special(".X3Tk0"), 1)

    def test_non_ascii(self):
        self.assertEqual(Metrics.non_ascii("cfvu rovit nzmyz qwhtnh ey lauyfdiv"), 0)
        self.assertEqual(Metrics.non_ascii("L!U'[N(a#QCMJ9EH"), 0)
        self.assertEqual(Metrics.non_ascii("`%!)@:rN^4W'"), 0)
        self.assertEqual(Metrics.non_ascii("PGZs4@y2"), 0)
        self.assertEqual(Metrics.non_ascii("yjjmqkuevd"), 0)
        self.assertEqual(Metrics.non_ascii("CDMZXLVWTF"), 0)
        self.assertEqual(Metrics.non_ascii("9105609999"), 0)
        self.assertEqual(Metrics.non_ascii("[&:/>!</|<"), 0)

        self.assertEqual(Metrics.non_ascii("2uPV⍳V)=I`Y"), 1)
        self.assertEqual(Metrics.non_ascii(".X3TVα⍳Vk0"), 2)

    def test_entropy(self):
        self.assertEqual(Metrics.entropy("cfvu rovit nzmyz qwhtnh ey lauyfdiv"), 4.1)
        self.assertEqual(Metrics.entropy("L!U'[N(a#QCMJ9EH"), 4)
        self.assertEqual(Metrics.entropy("`%!)@:rN^4W'"), 3.6)
        self.assertEqual(Metrics.entropy("PGZs4@y2"), 3)
        self.assertEqual(Metrics.entropy("yjjmqkuevd"), 3.1)
        self.assertEqual(Metrics.entropy("CDMZXLVWTF"), 3.3)
        self.assertEqual(Metrics.entropy("9105609999"), 2)
        self.assertEqual(Metrics.entropy("[&:/>!</|<"), 2.9)
        self.assertEqual(Metrics.entropy("2uPI`Y"), 2.6)
        self.assertEqual(Metrics.entropy(".X3Tk0"), 2.6)

    def test_repeats(self):
        self.assertEqual(Metrics.repeats("cfvu rovit nzmyz qwhtnh ey lauyfdiv"), 0)
        self.assertEqual(Metrics.repeats("L!U'[N(a#QCMJ9EH"), 0)
        self.assertEqual(Metrics.repeats("`%!)@:rN^4W'"), 0)
        self.assertEqual(Metrics.repeats("PGZs4@y2"), 0)
        self.assertEqual(Metrics.repeats("yjjmqkuevd"), 2)
        self.assertEqual(Metrics.repeats("CDMZXLVWTF"), 0)
        self.assertEqual(Metrics.repeats("9105609999"), 4)
        self.assertEqual(Metrics.repeats("[&:/>!</|<"), 0)
        self.assertEqual(Metrics.repeats("2uPI`Y"), 0)
        self.assertEqual(Metrics.repeats(".X3Tk0"), 0)

        self.assertEqual(Metrics.repeats("2uPPPI`Y"), 3)
        self.assertEqual(Metrics.repeats(".X3333Tk0"), 4)

    def test_sequence(self):
        self.assertEqual(Metrics.sequences("cfvu rovit nzmyz qwhtnh ey lauyfdiv"), 0)
        self.assertEqual(Metrics.sequences("L!U'[N(a#QCMJ9EH"), 1)
        self.assertEqual(Metrics.sequences("`%!)@:rN^4W'"), 1)
        self.assertEqual(Metrics.sequences("PGZs4@y2"), 1)
        self.assertEqual(Metrics.sequences("yjjmqkuevd"), 0)
        self.assertEqual(Metrics.sequences("CDMZXLVWTF"), 0)
        self.assertEqual(Metrics.sequences("9105609999"), 2)
        self.assertEqual(Metrics.sequences("[&:/>!</|<"), 0)
        self.assertEqual(Metrics.sequences("2uPI`Y"), 1)
        self.assertEqual(Metrics.sequences(".X3Tk0"), 1)

        self.assertEqual(Metrics.sequences("2u123I`Y"), 3)
        self.assertEqual(Metrics.sequences(".X43213333Tk0"), 4)

    def test_similarity(self):
        self.assertLess(Metrics.similarity("cfvu rovit nzmyz qwhtnh ey lauyfdiv"), .35)
        self.assertLess(Metrics.similarity("L!U'[N(a#QCMJ9EH"), 0.37)
        self.assertLess(Metrics.similarity("`%!)@:rN^4W'"), 0.35)
        self.assertLess(Metrics.similarity("PGZs4@y2"), 0.47)
        self.assertLess(Metrics.similarity("yjjmqkuevd"), 0.45)
        self.assertLess(Metrics.similarity("CDMZXLVWTF"), 0.45)
        self.assertLess(Metrics.similarity("9105609999"), 0.6)
        self.assertLess(Metrics.similarity("[&:/>!</|<"), 0.45)
        self.assertLess(Metrics.similarity("2uPI`Y"), 0.51)
        self.assertLess(Metrics.similarity(".X3Tk0"), 0.51)

        self.assertAlmostEqual(Metrics.similarity("password"), 1, 1)
        self.assertAlmostEqual(Metrics.similarity("sgdpassword"), .84, 1)
        self.assertAlmostEqual(Metrics.similarity("password123"), .9, 1)
        self.assertAlmostEqual(Metrics.similarity("123password"), .84, 1)
        self.assertAlmostEqual(Metrics.similarity("123password123"), .78, 1)
        self.assertAlmostEqual(Metrics.similarity("mysillypassword"), .69, 1)


    def test_contains(self):
        self.assertEqual(Metrics.contains("cfvu rovit nzmyz qwhtnh ey lauyfdiv"), 0)
        self.assertEqual(Metrics.contains("L!U'[N(a#QCMJ9EH"), 0)
        self.assertEqual(Metrics.contains("`%!)@:rN^4W'"), 0)
        self.assertEqual(Metrics.contains("PGZs4@y2"), 0)
        self.assertEqual(Metrics.contains("yjjmqkuevd"), 0)
        self.assertEqual(Metrics.contains("CDMZXLVWTF"), 0)
        self.assertEqual(Metrics.contains("9105609999"), 1)
        self.assertEqual(Metrics.contains("[&:/>!</|<"), 0)
        self.assertEqual(Metrics.contains("2uPI`Y"), 0)
        self.assertEqual(Metrics.contains(".X3Tk0"), 0)

        self.assertEqual(Metrics.contains("password"), 2)
        self.assertEqual(Metrics.contains("password123"), 3)
        self.assertEqual(Metrics.contains("pepperpassword"), 3)

