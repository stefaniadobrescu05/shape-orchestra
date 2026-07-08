"""OSC transport for the Machine 1 feature stream."""

# Import the UDP client class that sends OSC packets over the network.
from pythonosc.udp_client import SimpleUDPClient

# Import the official feature order so every sender builds the same packet layout.
from feature_extractor import FEATURE_NAMES


def build_feature_payload(features):
    """Build the ordered list of floats expected by Machine 2."""
    missing_features = set(FEATURE_NAMES) - set(features)  # Find required feature names that are absent.
    if missing_features:  # Stop early if the caller forgot a feature.
        missing = ", ".join(sorted(missing_features))  # Make the missing names readable in the error.
        raise ValueError(f"Cannot build OSC payload; missing: {missing}.")

    return [float(features[name]) for name in FEATURE_NAMES]  # Convert the dict into Wekinator's expected order.


class OscFeatureSender:
    """Send feature dictionaries as UDP OSC messages."""

    def __init__(self, destination_ip, destination_port, address):
        if not address.startswith("/"):  # OSC addresses must begin with a slash, for example /shape/features.
            raise ValueError("An OSC address must start with '/'.")

        self.destination_ip = destination_ip  # Store the IP so debug/tests can inspect where packets go.
        self.destination_port = destination_port  # Store the UDP port used by the OSC receiver.
        self.address = address  # Store the OSC address used for each message.
        self._client = SimpleUDPClient(destination_ip, destination_port)  # Create the actual UDP OSC client.

    def send(self, features):
        """Send one feature packet and return its payload for diagnostics."""
        payload = build_feature_payload(features)  # Turn the feature dictionary into a numeric list.
        self._client.send_message(self.address, payload)  # Send the list to Machine 2 through OSC over UDP.
        return payload  # Return the sent values so tests or logs can verify them.
