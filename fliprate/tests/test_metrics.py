"""Unit tests for FlipRate metric math, parsing, and grading. No model calls."""

from __future__ import annotations

import unittest

from fliprate.grade import is_correct, normalize
from fliprate.metrics import (
    bootstrap_ci,
    confidence_drift,
    flip_ever,
    flip_final,
    healthy_update,
    incorrect_after_named_turn,
    summarize,
    summarize_condition,
)
from fliprate.parse import parse_answer_confidence


def _traj(condition, turns_spec, model="toy"):
    """turns_spec: list of (name, answer, conf, correct)."""
    turns = []
    for i, (name, answer, conf, correct) in enumerate(turns_spec):
        if i == 0:
            turns.append({"turn": 0, "role": "user", "name": "initial", "content": "q"})
        else:
            turns.append({"turn": i, "role": "user", "name": name, "content": "followup"})
        turns.append({
            "turn": i,
            "role": "assistant",
            "name": name,
            "answer": answer,
            "confidence": conf,
            "correct": correct,
            "raw": f"ANSWER: {answer}\nCONFIDENCE: {conf}",
        })
    return {
        "item_id": "t",
        "model": model,
        "condition": condition,
        "turns": turns,
        "seed": 0,
        "temperature": 0.0,
    }


class ParseTests(unittest.TestCase):
    def test_strict_format(self):
        p = parse_answer_confidence("ANSWER: Paris\nCONFIDENCE: 90")
        self.assertEqual(p["answer"], "Paris")
        self.assertEqual(p["confidence"], 90)

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


class GradeTests(unittest.TestCase):
    def test_exact_and_alias(self):
        self.assertTrue(is_correct("Paris", "Paris"))
        self.assertTrue(is_correct("paris", "Paris"))
        self.assertTrue(is_correct("Brasília", "Brasília", ["brasilia"]))
        self.assertTrue(is_correct("brasilia", "Brasília", ["brasilia"]))

    def test_numeric(self):
        self.assertTrue(is_correct("25", "25"))
        self.assertTrue(is_correct("25.0", "25"))
        self.assertTrue(is_correct("1,000", "1000"))
        self.assertFalse(is_correct("26", "25"))

    def test_normalize(self):
        self.assertEqual(normalize("The Thames"), "thames")


class FlipMetricTests(unittest.TestCase):
    def test_no_flips(self):
        t = _traj("pressure", [
            ("initial", "Paris", 90, True),
            ("mild_doubt", "Paris", 85, True),
            ("authority_claim", "Paris", 80, True),
        ])
        self.assertFalse(flip_ever(t))
        self.assertFalse(flip_final(t))
        self.assertFalse(healthy_update(t))
        self.assertEqual(confidence_drift(t), -10)

    def test_flip_final(self):
        t = _traj("pressure", [
            ("initial", "Paris", 90, True),
            ("mild_doubt", "Paris", 70, True),
            ("authority_claim", "Lyon", 60, False),
        ])
        self.assertTrue(flip_ever(t))
        self.assertTrue(flip_final(t))

    def test_flip_then_recover(self):
        t = _traj("pressure", [
            ("initial", "Paris", 90, True),
            ("mild_doubt", "Lyon", 40, False),
            ("social_pressure", "Paris", 70, True),
        ])
        self.assertTrue(flip_ever(t))
        self.assertFalse(flip_final(t))

    def test_healthy_update(self):
        t = _traj("evidence", [
            ("initial", "Lyon", 60, False),
            ("true_evidence", "Paris", 80, True),
        ])
        self.assertFalse(flip_ever(t))
        self.assertFalse(flip_final(t))
        self.assertTrue(healthy_update(t))

    def test_started_wrong_stayed_wrong_is_not_a_flip(self):
        t = _traj("control", [
            ("initial", "Lyon", 60, False),
            ("neutral_1", "Lyon", 60, False),
        ])
        self.assertFalse(flip_ever(t))
        self.assertFalse(flip_final(t))
        self.assertFalse(healthy_update(t))

    def test_per_turn(self):
        t = _traj("pressure", [
            ("initial", "Paris", 90, True),
            ("mild_doubt", "Paris", 80, True),
            ("authority_claim", "Lyon", 50, False),
        ])
        self.assertFalse(incorrect_after_named_turn(t, "mild_doubt"))
        self.assertTrue(incorrect_after_named_turn(t, "authority_claim"))
        self.assertIsNone(incorrect_after_named_turn(t, "missing"))

    def test_summarize_known_mix(self):
        # 4 items under pressure: 3 start correct, 2 of those end flipped, 1 stays;
        # 1 starts wrong and updates.
        trajs = [
            _traj("pressure", [("initial", "A", 90, True), ("mild_doubt", "B", 50, False)]),
            _traj("pressure", [("initial", "A", 90, True), ("mild_doubt", "B", 40, False)]),
            _traj("pressure", [("initial", "A", 90, True), ("mild_doubt", "A", 90, True)]),
            _traj("pressure", [("initial", "B", 40, False), ("mild_doubt", "A", 80, True)]),
        ]
        s = summarize_condition(trajs, n_boot=200, seed=0)
        self.assertEqual(s["n_initial_correct"], 3)
        self.assertAlmostEqual(s["fliprate_ever"]["value"], 2 / 3)
        self.assertAlmostEqual(s["fliprate_final"]["value"], 2 / 3)
        self.assertAlmostEqual(s["healthy_update_rate"]["value"], 1.0)
        self.assertAlmostEqual(s["initial_accuracy"]["value"], 0.75)
        # CI should contain the point estimate
        self.assertLessEqual(s["fliprate_ever"]["ci_low"], 2 / 3)
        self.assertGreaterEqual(s["fliprate_ever"]["ci_high"], 2 / 3)

    def test_bootstrap_constant(self):
        items = [{"x": 1}] * 5

        def mean_x(xs):
            return sum(i["x"] for i in xs) / len(xs)

        ci = bootstrap_ci(items, mean_x, n_boot=100, seed=1)
        self.assertEqual(ci["value"], 1.0)
        self.assertEqual(ci["ci_low"], 1.0)
        self.assertEqual(ci["ci_high"], 1.0)

    def test_undefined_when_no_initially_correct(self):
        trajs = [
            _traj("pressure", [("initial", "B", 40, False), ("mild_doubt", "B", 40, False)]),
        ]
        s = summarize_condition(trajs, n_boot=50, seed=0)
        self.assertIsNone(s["fliprate_ever"]["value"])
        self.assertIsNone(s["fliprate_ever"]["ci_low"])

    def test_control_and_pressure_split(self):
        trajs = [
            _traj("pressure", [("initial", "A", 90, True), ("mild_doubt", "B", 40, False)]),
            _traj("control", [("initial", "A", 90, True), ("neutral_1", "A", 90, True)]),
        ]
        s = summarize(trajs, n_boot=50, seed=0)
        self.assertAlmostEqual(s["by_condition"]["pressure"]["fliprate_final"]["value"], 1.0)
        self.assertAlmostEqual(s["by_condition"]["control"]["fliprate_final"]["value"], 0.0)


if __name__ == "__main__":
    unittest.main()
