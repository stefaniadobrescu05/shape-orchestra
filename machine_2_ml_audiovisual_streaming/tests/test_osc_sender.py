from pythonosc.udp_client import SimpleUDPClient

OSC_IP = "127.0.0.1" # adresa locala a calculatorului
OSC_PORT = 12000 # portul pe care asculta Processing
OSC_ADDRESS = "/shape/control"# adresa OSC asteptata de Processing

client = SimpleUDPClient(OSC_IP, OSC_PORT)# creez clientul OSC

print("Shape Orchestra OSC Test Sender")
print("1 = CALM")
print("2 = PULSE")
print("3 = TENSION")
print("4 = CLIMAX")
print("q = quit")


while True:
    command = input("\nState: ").strip()
    # opresc programul
    if command.lower() == "q":
        print("Test sender stopped")
        break
    try:
        # citesc starea
        state = int(command)
        # verific starea
        if state < 1 or state > 4:
            print("State must be between 1 and 4")
            continue
        # citesc intensitatea
        intensity = float(
            input("Intensity [0.0 - 1.0]: ")
        )
        # verific intensitatea
        if intensity < 0.0 or intensity > 1.0:
            print("Intensity must be between 0.0 and 1.0")
            continue
        # trimit mesajul OSC
        client.send_message(
            OSC_ADDRESS,
            [float(state), float(intensity)]
        )
        print(
            f"Sent -> state: {state}"
            f" | intensity: {intensity:.3f}"
        )
    except ValueError:
        print("Invalid numeric value")