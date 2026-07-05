"""OSC transport for the Machine 1 feature stream."""

from pythonosc.udp_client import SimpleUDPClient

from feature_extractor import FEATURE_NAMES


def build_feature_payload(features):
    """Build the ordered list of floats expected by Machine 2."""
    missing_features = set(FEATURE_NAMES) - set(features)
    if missing_features:
        missing = ", ".join(sorted(missing_features))
        raise ValueError(f"Cannot build OSC payload; missing: {missing}.")

    return [float(features[name]) for name in FEATURE_NAMES]


class OscFeatureSender:
    """Send feature dictionaries as UDP OSC messages."""

    def __init__(self, destination_ip, destination_port, address):
        if not address.startswith("/"):
            raise ValueError("An OSC address must start with '/'.")

        self.destination_ip = destination_ip
        self.destination_port = destination_port
        self.address = address
        self._client = SimpleUDPClient(destination_ip, destination_port)

    def send(self, features):
        """Send one feature packet and return its payload for diagnostics."""
        payload = build_feature_payload(features)
        self._client.send_message(self.address, payload)
        return payload
