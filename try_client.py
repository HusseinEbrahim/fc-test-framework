from msp_client import MSPClient, find_flight_controller

port = find_flight_controller()
print("Found flight controller on", port)

fc = MSPClient(port)
try:
    print("API version:", fc.api_version())
    print("Firmware:   ", fc.fc_variant(), fc.fc_version())
    print("Power:      ", fc.analog())
    print("Attitude:   ", fc.attitude())
finally:
    fc.close()