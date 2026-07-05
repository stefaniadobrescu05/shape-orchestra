"""Tests for Machine 1 feature extraction and smoothing."""

from pathlib import Path
from types import SimpleNamespace
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from feature_extractor import (  # noqa: E402
    FEATURE_NAMES,
    FeatureSmoother,
    HandFeatureExtractor,
)


def make_hand(translation_x=0.0):
    """Create a small MediaPipe-like hand object for deterministic tests."""
    landmarks = [
        SimpleNamespace(x=0.5 + translation_x, y=0.5, z=0.0)
        for _ in range(21)
    ]
    landmarks[9] = SimpleNamespace(x=0.5 + translation_x, y=0.3, z=0.0)

    fingertip_positions = {
        4: (0.30, 0.35),
        8: (0.40, 0.15),
        12: (0.50, 0.10),
        16: (0.60, 0.15),
        20: (0.70, 0.25),
    }
    for index, (x, y) in fingertip_positions.items():
        landmarks[index] = SimpleNamespace(
            x=x + translation_x,
            y=y,
            z=0.0,
        )

    return SimpleNamespace(landmark=landmarks)


class HandFeatureExtractorTests(unittest.TestCase):
    def test_extracts_complete_feature_set(self):
        extractor = HandFeatureExtractor()

        features = extractor.extract(make_hand())

        self.assertEqual(tuple(features), FEATURE_NAMES)
        self.assertEqual(features["speed"], 0.0)
        self.assertGreater(features["openness"], 0.0)

    def test_motion_uses_change_between_frames(self):
        extractor = HandFeatureExtractor()
        first = extractor.extract(make_hand())
        second = extractor.extract(make_hand(translation_x=0.1))

        self.assertAlmostEqual(second["direction_x"], 0.1)
        self.assertAlmostEqual(second["direction_y"], 0.0)
        self.assertAlmostEqual(second["speed"], 0.1)
        self.assertAlmostEqual(second["openness"], first["openness"])
        self.assertAlmostEqual(
            second["energy"],
            second["speed"] * second["openness"],
        )

    def test_reset_prevents_reacquisition_speed_spike(self):
        extractor = HandFeatureExtractor()
        extractor.extract(make_hand())
        extractor.reset()

        features = extractor.extract(make_hand(translation_x=0.4))

        self.assertEqual(features["speed"], 0.0)

    def test_dead_zone_ignores_jitter_but_accumulates_slow_motion(self):
        extractor = HandFeatureExtractor(movement_dead_zone=0.05)
        extractor.extract(make_hand())

        jitter = extractor.extract(make_hand(translation_x=0.02))
        accumulated_motion = extractor.extract(make_hand(translation_x=0.06))

        self.assertEqual(jitter["speed"], 0.0)
        self.assertAlmostEqual(accumulated_motion["speed"], 0.06)


class FeatureSmootherTests(unittest.TestCase):
    def test_exponential_smoothing_reduces_a_sudden_change(self):
        smoother = FeatureSmoother(0.2)
        zeros = {name: 0.0 for name in FEATURE_NAMES}
        ones = {name: 1.0 for name in FEATURE_NAMES}

        smoother.update(zeros)
        smoothed = smoother.update(ones)

        for value in smoothed.values():
            self.assertAlmostEqual(value, 0.2)

    def test_reset_accepts_the_next_frame_without_old_history(self):
        smoother = FeatureSmoother(0.2)
        smoother.update({name: 0.0 for name in FEATURE_NAMES})
        smoother.reset()

        features = {name: 1.0 for name in FEATURE_NAMES}

        self.assertEqual(smoother.update(features), features)

    def test_dead_bands_hold_small_smoothed_changes(self):
        dead_bands = {name: 0.1 for name in FEATURE_NAMES}
        smoother = FeatureSmoother(1.0, dead_bands)
        zeros = {name: 0.0 for name in FEATURE_NAMES}
        small_change = {name: 0.05 for name in FEATURE_NAMES}
        meaningful_change = {name: 0.2 for name in FEATURE_NAMES}

        smoother.update(zeros)

        self.assertEqual(smoother.update(small_change), zeros)
        self.assertEqual(smoother.update(meaningful_change), meaningful_change)


if __name__ == "__main__":
    unittest.main()
