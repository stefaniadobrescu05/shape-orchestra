"""Tests for the Machine 1 OSC message contract."""

from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from feature_extractor import FEATURE_NAMES  # noqa: E402
from osc_sender import OscFeatureSender, build_feature_payload  # noqa: E402


class OscSenderTests(unittest.TestCase):
    def setUp(self):
        self.features = {
            name: float(index)
            for index, name in enumerate(FEATURE_NAMES, start=1)
        }

    def test_payload_follows_the_documented_feature_order(self):
        self.assertEqual(
            build_feature_payload(self.features),
            [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
        )

    @patch("osc_sender.SimpleUDPClient")
    def test_sender_uses_configured_address_and_udp_destination(self, client_class):
        sender = OscFeatureSender("192.168.1.20", 6448, "/shape/features")

        payload = sender.send(self.features)

        client_class.assert_called_once_with("192.168.1.20", 6448)
        client_class.return_value.send_message.assert_called_once_with(
            "/shape/features",
            payload,
        )

    def test_missing_feature_is_rejected(self):
        incomplete_features = self.features.copy()
        del incomplete_features["energy"]

        with self.assertRaisesRegex(ValueError, "energy"):
            build_feature_payload(incomplete_features)


if __name__ == "__main__":
    unittest.main()
