from msp_client import open_real_board

fc = open_real_board()
try:
    print("API version:", fc.api_version())
    print("Firmware:   ", fc.fc_variant(), fc.fc_version())
    print("Power:      ", fc.analog())
    print("Attitude:   ", fc.attitude())
finally:
    fc.close()