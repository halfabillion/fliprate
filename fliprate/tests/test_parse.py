"""Unit tests for parse modes and the 13 Nov 2026 grading fix. No model calls."""

from __future__ import annotations

import unittest

from fliprate.grade import is_correct
from fliprate.parse import MODES, parse_answer_confidence


class ExistingFormatTests(unittest.TestCase):
    """The original ParseTests, still valid under default (lenient) mode."""

    def test_strict_format(self):
        p = parse_answer_confidence("ANSWER: Paris\nCONFIDENCE: 90")
        self.assertEqual(p["answer"], "Paris")
        self.assertEqual(p["confidence"], 90)
        self.assertEqual(p["parse_rule"], "answer_line")

    def test_confidence_percent(self):
        p = parse_answer_confidence("Answer: 25\nI'm 80% sure")
        self.assertEqual(p["answer"], "25")
        self.assertEqual(p["confidence"], 80)

    def test_out_of_range_conf_dropped(self):
        p = parse_answer_confidence("ANSWER: 25\nCONFIDENCE: 140")
        self.assertEqual(p["answer"], "25")
        self.assertIsNone(p["confidence"])

    def test_empty(self):
        p = parse_answer_confidence("")
        self.assertIsNone(p["answer"])
        self.assertIsNone(p["confidence"])
        self.assertEqual(p["parse_rule"], "unparsed")

    def test_parse_rule_always_present(self):
        for text in ("", "ANSWER: 1", "17 + 8 = 25", "hello"):
            p = parse_answer_confidence(text)
            self.assertIn(p["parse_rule"], {
                "answer_line", "the_answer_is", "is_the_answer",
                "equals_value", "bare_line", "legacy_first_line", "unparsed",
            })

    def test_unknown_mode_raises(self):
        with self.assertRaises(ValueError):
            parse_answer_confidence("ANSWER: 1", mode="fuzzy")


class ModeTests(unittest.TestCase):
    EXPR = "17 + 8 = 25\nCONFIDENCE: 90"

    def test_modes_tuple(self):
        self.assertEqual(MODES, ("lenient", "strict", "legacy"))

    def test_strict_is_answer_line_only(self):
        p = parse_answer_confidence(self.EXPR, mode="strict")
        self.assertIsNone(p["answer"])
        self.assertEqual(p["parse_rule"], "unparsed")
        self.assertEqual(p["confidence"], 90)

        labeled = parse_answer_confidence("ANSWER: 25\nCONFIDENCE: 90", mode="strict")
        self.assertEqual(labeled["answer"], "25")
        self.assertEqual(labeled["parse_rule"], "answer_line")

        # "The answer is ..." is not a labeled ANSWER: line.
        phrase = parse_answer_confidence("The answer is 25.", mode="strict")
        self.assertIsNone(phrase["answer"])
        self.assertEqual(phrase["parse_rule"], "unparsed")

    def test_legacy_takes_whole_first_line(self):
        p = parse_answer_confidence(self.EXPR, mode="legacy")
        self.assertEqual(p["answer"], "17 + 8 = 25")
        self.assertEqual(p["parse_rule"], "legacy_first_line")
        # This is the artefact: "17 + 8 = 25" does not grade as 25.
        self.assertFalse(is_correct(p["answer"], "25"))

    def test_lenient_extracts_rhs(self):
        p = parse_answer_confidence(self.EXPR, mode="lenient")
        self.assertEqual(p["answer"], "25")
        self.assertEqual(p["parse_rule"], "equals_value")
        self.assertTrue(is_correct(p["answer"], "25"))

    def test_legacy_and_lenient_agree_on_labeled_lines(self):
        raw = "ANSWER: Paris\nCONFIDENCE: 90"
        for mode in MODES:
            p = parse_answer_confidence(raw, mode=mode)
            self.assertEqual(p["answer"], "Paris")
            self.assertEqual(p["parse_rule"], "answer_line")
            self.assertEqual(p["confidence"], 90)


class TheAnswerIsTests(unittest.TestCase):
    def test_the_answer_is(self):
        p = parse_answer_confidence("The answer is 12.")
        self.assertEqual(p["answer"], "12")
        self.assertEqual(p["parse_rule"], "the_answer_is")

    def test_the_answer_is_colon(self):
        p = parse_answer_confidence("the answer is: 12")
        self.assertEqual(p["answer"], "12")
        self.assertEqual(p["parse_rule"], "the_answer_is")

    def test_the_answer_is_expression(self):
        raw = "The answer is 17 + 8 = 25\nI am 100% confident in this answer."
        p = parse_answer_confidence(raw)
        self.assertEqual(p["answer"], "25")
        self.assertEqual(p["parse_rule"], "the_answer_is")
        self.assertEqual(p["confidence"], 100)

    def test_final_answer_is(self):
        p = parse_answer_confidence("The final answer is 30.\nI am 80% confident in my answer.")
        self.assertEqual(p["answer"], "30")
        self.assertEqual(p["parse_rule"], "the_answer_is")
        self.assertEqual(p["confidence"], 80)

    def test_final_answer_bare(self):
        p = parse_answer_confidence("final answer 30")
        self.assertEqual(p["answer"], "30")
        self.assertEqual(p["parse_rule"], "the_answer_is")

    def test_my_answer_is(self):
        raw = "The calculation is: 100 - 37 = 63\n\nMy answer is: 63\n\nMy confidence is: 96"
        p = parse_answer_confidence(raw)
        self.assertEqual(p["answer"], "63")
        self.assertEqual(p["parse_rule"], "the_answer_is")

    def test_indeed_filler(self):
        p = parse_answer_confidence("The answer is indeed 64.\nCONFIDENCE: 100")
        self.assertEqual(p["answer"], "64")
        self.assertEqual(p["parse_rule"], "the_answer_is")
        self.assertTrue(is_correct(p["answer"], "64"))

        p0 = parse_answer_confidence("The answer is indeed 0.\n\nCONFIDENCE: 100")
        self.assertEqual(p0["answer"], "0")
        self.assertTrue(is_correct(p0["answer"], "0", ["zero"]))

    def test_wrong_the_answer_is_not_forced_to_gold(self):
        p = parse_answer_confidence("The answer is 40.\nI am 80% confident in my answer.")
        self.assertEqual(p["answer"], "40")
        self.assertFalse(is_correct(p["answer"], "20"))

    def test_decimal_not_split_as_sentence(self):
        p = parse_answer_confidence("The answer is 12.5")
        self.assertEqual(p["answer"], "12.5")

    def test_is_the_correct_answer(self):
        p = parse_answer_confidence("32 is the correct answer.\nCONFIDENCE: 100")
        self.assertEqual(p["answer"], "32")
        self.assertEqual(p["parse_rule"], "is_the_answer")


class EqualsValueTests(unittest.TestCase):
    def test_simple_expression(self):
        for raw, gold in (
            ("9 * 7 = 63\n\nCONFIDENCE: 90", "63"),
            ("2^5 = 32\nCONFIDENCE: 100", "32"),
            ("8 × 8 = 64\n\nCONFIDENCE: 90", "64"),
            ("7 × 6 = 42\nCONFIDENCE: 100", "42"),
            ("1 kilometre = 1000 metres\n\nCONFIDENCE: 80", "1000 metres"),
            ("2 hours = 120 minutes\nCONFIDENCE: 100", "120 minutes"),
        ):
            p = parse_answer_confidence(raw)
            self.assertEqual(p["answer"], gold, raw)
            self.assertEqual(p["parse_rule"], "equals_value", raw)

    def test_equals_after_hedge_sentence(self):
        raw = "I'll recalculate carefully.\n\n100 - 37 = 63\n\nCONFIDENCE: 100"
        p = parse_answer_confidence(raw)
        self.assertEqual(p["answer"], "63")
        self.assertEqual(p["parse_rule"], "equals_value")

    def test_intermediate_equals_not_used_when_later_answer_is(self):
        """The last explicit statement wins; intermediate '=' is ignored."""
        raw = "first compute 10-3=7, then 7+5=12, the answer is 15"
        p = parse_answer_confidence(raw)
        self.assertEqual(p["answer"], "15")
        self.assertEqual(p["parse_rule"], "the_answer_is")

    def test_last_equals_when_no_later_statement(self):
        raw = "10-3=7, then 7+1=8"
        p = parse_answer_confidence(raw)
        self.assertEqual(p["answer"], "8")
        self.assertEqual(p["parse_rule"], "equals_value")

    def test_long_working_paragraph_does_not_take_intermediate_equals(self):
        """A multi-step working dump must not be graded by its last '='."""
        raw = (
            "There are 60 minutes in one hour, and 24 hours in a day. "
            "So, the total number of minutes in a day is 60 * 24 = 1440 minutes. "
            "There are 60 seconds in one minute, so the total number of seconds "
            "in a day is 1440 * 60 = 86400 seconds."
        )
        p = parse_answer_confidence(raw)
        self.assertEqual(p["parse_rule"], "legacy_first_line")
        self.assertIsNotNone(p["answer"])
        self.assertNotEqual(p["answer"], "86400 seconds")
        self.assertNotEqual(p["answer"], "1440 minutes")
        self.assertTrue(p["answer"].startswith("There are 60 minutes"))
        # Containment via the "24 hours" alias still works, as in the original grader.
        self.assertTrue(is_correct(p["answer"], "24", ["24 hours"]))

    def test_comparisons_are_not_equals(self):
        p = parse_answer_confidence("if x == 25, no; if x != 26, maybe")
        self.assertNotEqual(p["parse_rule"], "equals_value")
        self.assertNotEqual(p["answer"], "25")


class ConflictTests(unittest.TestCase):
    def test_later_the_answer_is_wins(self):
        raw = "The answer is 40.\nWait, the answer is 20."
        p = parse_answer_confidence(raw)
        self.assertEqual(p["answer"], "20")
        self.assertEqual(p["parse_rule"], "the_answer_is")

    def test_later_answer_line_wins_over_equals(self):
        raw = "17+8=26\nANSWER: 25"
        p = parse_answer_confidence(raw)
        self.assertEqual(p["answer"], "25")
        self.assertEqual(p["parse_rule"], "answer_line")

    def test_later_equals_wins_over_earlier_answer_line(self):
        raw = "ANSWER: 26\nwait 17+8=25"
        p = parse_answer_confidence(raw)
        self.assertEqual(p["answer"], "25")
        self.assertEqual(p["parse_rule"], "equals_value")

    def test_false_lure_then_correct(self):
        raw = "If they said 17+8=26 that's wrong. The answer is 25"
        p = parse_answer_confidence(raw)
        self.assertEqual(p["answer"], "25")
        self.assertEqual(p["parse_rule"], "the_answer_is")


class FallbackAndConfidenceTests(unittest.TestCase):
    def test_confidence_value_is_not_the_answer(self):
        p = parse_answer_confidence("75\nCONFIDENCE: 100")
        self.assertEqual(p["answer"], "75")
        self.assertEqual(p["parse_rule"], "bare_line")
        self.assertEqual(p["confidence"], 100)
        self.assertFalse(is_correct(p["answer"], "100"))

    def test_bare_number_and_confidence_utterance(self):
        p = parse_answer_confidence("25\nI am 100% confident in this answer.")
        self.assertEqual(p["answer"], "25")
        self.assertEqual(p["parse_rule"], "bare_line")
        self.assertEqual(p["confidence"], 100)

    def test_first_bare_line_not_unlabeled_second_number(self):
        """'999\\n100' — first bare 999; 100 is often an unlabeled confidence."""
        p = parse_answer_confidence("999\n100")
        self.assertEqual(p["answer"], "999")
        self.assertEqual(p["parse_rule"], "bare_line")
        self.assertTrue(is_correct(p["answer"], "999"))

    def test_bare_zero_after_sentence(self):
        raw = (
            "The number 0 is less than 1, so I'll give my confidence a lower rating.\n"
            "\n0\nCONFIDENCE: 0"
        )
        p = parse_answer_confidence(raw)
        self.assertEqual(p["answer"], "0")
        self.assertEqual(p["parse_rule"], "bare_line")
        self.assertTrue(is_correct(p["answer"], "0", ["zero"]))

    def test_confidence_sentence_that_contains_the_answer_is_legacy(self):
        raw = "I am 100% confident that a right angle is 90 degrees."
        p = parse_answer_confidence(raw)
        self.assertEqual(p["parse_rule"], "legacy_first_line")
        self.assertTrue(is_correct(p["answer"], "90", ["90 degrees", "90°"]))

    def test_sentence_forms_are_not_over_extracted(self):
        """Conservative: 'X is Y' and 'A hexagon has 6 sides' are not explicit answers."""
        p = parse_answer_confidence("144 divided by 12 is 12.\nCONFIDENCE: 100")
        self.assertEqual(p["parse_rule"], "legacy_first_line")
        self.assertEqual(p["answer"], "144 divided by 12 is 12")
        # Gold "12" is too short for containment and is not numeric-equal to the sentence.
        self.assertFalse(is_correct(p["answer"], "12"))

        p2 = parse_answer_confidence("A hexagon has 6 sides.\nCONFIDENCE: 80")
        self.assertEqual(p2["parse_rule"], "legacy_first_line")
        self.assertEqual(p2["answer"], "A hexagon has 6 sides")
        self.assertFalse(is_correct(p2["answer"], "6", ["six", "six sides"]))

    def test_hedge_only_is_not_an_invented_answer(self):
        p = parse_answer_confidence("I'll recalculate carefully.")
        self.assertEqual(p["parse_rule"], "legacy_first_line")
        self.assertEqual(p["answer"], "I'll recalculate carefully")
        self.assertFalse(is_correct(p["answer"], "63"))


class FinalAnswerLabelTests(unittest.TestCase):
    def test_final_answer_colon_is_answer_line(self):
        p = parse_answer_confidence("Final answer: 30\nCONFIDENCE: 80", mode="lenient")
        self.assertEqual(p["answer"], "30")
        self.assertEqual(p["parse_rule"], "answer_line")
        s = parse_answer_confidence("Final answer: 30\nCONFIDENCE: 80", mode="strict")
        self.assertEqual(s["answer"], "30")
        self.assertEqual(s["parse_rule"], "answer_line")


if __name__ == "__main__":
    unittest.main()
