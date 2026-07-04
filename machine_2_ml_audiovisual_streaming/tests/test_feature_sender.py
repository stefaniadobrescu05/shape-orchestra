from pythonosc.udp_client import SimpleUDPClient
import time

WEKINATOR_IP = "127.0.0.1" # adresa locala a calculatorului
WEKINATOR_PORT = 6448 # portul de input configurat in Wekinator
OSC_ADDRESS = "/shape/features" # adresa OSC asteptata de Wekinator

# creez clientul OSC
client = SimpleUDPClient(
    WEKINATOR_IP,
    WEKINATOR_PORT
)
# valori de test pentru cele 7 feature-uri
features=[
    0.50,   # hand_x
    0.50,   # hand_y
    0.20,   # speed
    0.01,   # direction_x
    -0.02,  # direction_y
    0.70,   # openness
    0.35    # energy
]

print("Shape Orchestra Feature Test Sender")
print("Sending...")
print(f"Address: {OSC_ADDRESS}")
print(f"Features: {features}")

try:
    while True:
        # trimit cele 7 feature-uri
        client.send_message(OSC_ADDRESS,features)
        # aproximativ 20 mesaje pe secunda
        time.sleep(0.05)
except KeyboardInterrupt:
    print("\nStopped")