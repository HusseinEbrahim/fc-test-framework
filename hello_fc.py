import serial
import struct

PORT = "COM7"

def msp_request(command):
    size = 0
    checksum = size ^ command
    return bytes([36, 77, 60, size, command, checksum])

def parse_reply(reply, expected_command):

    if len(reply) < 6:
        raise ValueError("No reply or reply too short")


    if reply[0:3] != bytes([36, 77, 62]):
        raise ValueError("Bad header")

    size = reply[3]
    command = reply[4]
    payload = reply[5:5 + size]
    received_checksum = reply[5 + size]

    if command != expected_command:
        raise ValueError(f"Expected command {expected_command}, got {command}")

    checksum = size ^ command
    for b in payload:
        checksum = checksum ^ b

    if checksum != received_checksum:
        raise ValueError("Checksum mismatch: data corrupted")

    return payload

print("1. Opening port...")
with serial.Serial(PORT, 115200, timeout=1, write_timeout=2) as fc:
    print("2. Port open. Sending request...")
    fc.write(msp_request(1))
    print("3. Request sent. Waiting for reply...")
    reply = fc.read(64)
    print("4. Raw reply:", list(reply))

    payload = parse_reply(reply, 1)
    protocol, major, minor = struct.unpack("<BBB", payload[:3])
    print(f"API version {major}.{minor}")

print("\n--- Validation tests ---")

good = bytes([36, 77, 62, 3, 1, 0, 1, 46, 45])
bad_cases = {
    "empty reply":        bytes([]),
    "wrong header":       bytes([36, 77, 33, 3, 1, 0, 1, 46, 45]),
    "wrong command":      bytes([36, 77, 62, 3, 2, 0, 1, 46, 46]),
    "corrupted byte":     bytes([36, 77, 62, 3, 1, 0, 1, 47, 45]),
}

print("good reply ->", list(parse_reply(good, 1)))

for name, data in bad_cases.items():
    try:
        parse_reply(data, 1)
        print(f"{name}: NOT caught  ❌")
    except ValueError as e:
        print(f"{name}: caught ✅ ({e})")