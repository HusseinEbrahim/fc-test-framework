from checks import attitude_spread

def test_board_responds(fc):
    assert fc.api_version()


def test_api_version_supported(fc):
    major, minor = map(int, fc.api_version().split("."))
    assert (major, minor) >= (1, 46), f"API {major}.{minor} is older than supported 1.46"


def test_firmware_is_betaflight(fc):
    assert fc.fc_variant() == "BTFL"


def test_firmware_version_format(fc):
    parts = fc.fc_version().split(".")
    assert len(parts) == 3 and all(p.isdigit() for p in parts)


def test_voltage_in_safe_range(fc):
    voltage = fc.analog()["voltage"]
    assert 0 <= voltage <= 26.0, f"Voltage {voltage}V outside 0–26V (6S max is 25.2V)"


def test_attitude_within_physical_limits(fc):
    a = fc.attitude()
    assert -180 <= a["roll"] <= 180
    assert -90 <= a["pitch"] <= 90
    assert 0 <= a["yaw"] < 360


def test_gyro_stable_at_rest(fc):
    roll_spread, pitch_spread = attitude_spread(fc)
    assert roll_spread < 2.0, f"Roll varied {roll_spread:.1f}° at rest (limit 2°)"
    assert pitch_spread < 2.0, f"Pitch varied {pitch_spread:.1f}° at rest (limit 2°)"


def test_repeated_requests_are_reliable(fc):
    for i in range(50):
        assert fc.api_version() == "1.46", f"Failed on request {i + 1}"