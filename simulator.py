import struct


class SimulatedFC:
    """A fake flight controller that speaks MSP, like the real one."""

    def __init__(self, fault=None):
        self.fault = fault          # None, "no_reply", "bad_checksum", "wrong_command", "noisy_gyro"
        self.output = b""           # bytes waiting to be "read" by the client

        # The simulated board's state
        self.api = (0, 1, 46)
        self.variant = b"BTFL"
        self.version = (4, 5, 1)
        self.voltage = 0.11
        self.roll, self.pitch, self.yaw = -2.1, 1.3, 0

    # ---- the three methods MSPClient uses ----

    def reset_input_buffer(self):
        self.output = b""

    def write(self, data):
        command = data[4]
        self.output = self.build_reply(command)

    def read(self, size):
        data, self.output = self.output[:size], self.output[size:]
        return data

    def close(self):
        pass

    # ---- building replies ----

    def payload_for(self, command):
        if command == 1:
            return bytes(self.api)
        if command == 2:
            return self.variant
        if command == 3:
            return bytes(self.version)
        if command == 108:
            roll, pitch = self.roll, self.pitch
            if self.fault == "noisy_gyro":
                import random
                roll += random.uniform(-30, 30)
                pitch += random.uniform(-30, 30)
            return struct.pack("<hhh", int(roll * 10), int(pitch * 10), self.yaw)
        if command == 110:
            return struct.pack("<BHHhH", 0, 0, 0, 0, int(self.voltage * 100))
        return b""

    def build_reply(self, command):
        if self.fault == "no_reply":
            return b""

        payload = self.payload_for(command)
        size = len(payload)
        reply_command = command + 1 if self.fault == "wrong_command" else command

        checksum = size ^ reply_command
        for b in payload:
            checksum ^= b
        if self.fault == "bad_checksum":
            checksum ^= 0xFF  # flip every bit of the checksum

        return b"$M>" + bytes([size, reply_command]) + payload + bytes([checksum])