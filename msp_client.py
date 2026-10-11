import struct
import serial
from serial.tools import list_ports

# Command numbers (from Betaflight's MSP protocol)
MSP_API_VERSION = 1
MSP_FC_VARIANT = 2
MSP_FC_VERSION = 3
MSP_ATTITUDE = 108
MSP_ANALOG = 110


class MSPError(Exception):
    """Raised when the board's reply is missing or invalid."""


STM32_VID = 0x0483
STM32_PID = 0x5740


def find_flight_controller():
    for port in list_ports.comports():
        if port.vid == STM32_VID and port.pid == STM32_PID:
            return port.device
    raise MSPError("No flight controller found. Is it plugged in?")

class MSPClient:
    def __init__(self, port, baudrate=115200, timeout=1.0):
        self.serial = serial.Serial(port, baudrate, timeout=timeout, write_timeout=2)

    def close(self):
        self.serial.close()

    # ---------- low level: build, send, receive ----------

    @staticmethod
    def build_request(command):
        size = 0
        checksum = size ^ command
        return bytes([36, 77, 60, size, command, checksum])

    @staticmethod
    def parse_reply(reply, expected_command):
        if len(reply) < 6:
            raise MSPError("No reply or reply too short")
        if reply[0:3] != b"$M>":
            raise MSPError("Bad header")

        size = reply[3]
        command = reply[4]
        if len(reply) < 6 + size:
            raise MSPError("Reply shorter than its size byte says")

        payload = reply[5:5 + size]
        received_checksum = reply[5 + size]

        if command != expected_command:
            raise MSPError(f"Expected command {expected_command}, got {command}")

        checksum = size ^ command
        for b in payload:
            checksum ^= b
        if checksum != received_checksum:
            raise MSPError("Checksum mismatch: data corrupted")

        return payload

    def request(self, command):
        self.serial.reset_input_buffer()
        self.serial.write(self.build_request(command))
        reply = self.serial.read(64)
        return self.parse_reply(reply, command)

    # ---------- high level: one method per question ----------

    def api_version(self):
        payload = self.request(MSP_API_VERSION)
        protocol, major, minor = struct.unpack("<BBB", payload[:3])
        return f"{major}.{minor}"

    def fc_variant(self):
        payload = self.request(MSP_FC_VARIANT)
        return payload[:4].decode("ascii")

    def fc_version(self):
        payload = self.request(MSP_FC_VERSION)
        major, minor, patch = struct.unpack("<BBB", payload[:3])
        return f"{major}.{minor}.{patch}"

    def analog(self):
        payload = self.request(MSP_ANALOG)
        vbat, mah, rssi, amps, volts = struct.unpack("<BHHhH", payload[:9])
        return {
            "voltage": volts / 100,     # in volts
            "current": amps / 100,      # in amps
            "mah_drawn": mah,
            "rssi": rssi,
        }
    
    def attitude(self):
        payload = self.request(MSP_ATTITUDE)
        roll, pitch, yaw = struct.unpack("<hhh", payload[:6])
        return {
            "roll": roll/10,
            "pitch": pitch/10,
            "yaw": yaw,
        }   