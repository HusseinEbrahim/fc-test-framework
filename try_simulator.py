from msp_client import MSPClient, MSPError
from simulator import SimulatedFC

fc = MSPClient(SimulatedFC())
print("Healthy board:", fc.api_version(), fc.fc_variant(), fc.attitude())

for fault in ["no_reply", "bad_checksum", "wrong_command"]:
    fc = MSPClient(SimulatedFC(fault=fault))
    try:
        fc.api_version()
        print(f"{fault}: NOT detected ❌")
    except MSPError as e:
        print(f"{fault}: detected ✅ ({e})")