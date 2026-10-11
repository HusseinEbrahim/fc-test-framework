import pytest
from checks import attitude_spread
from msp_client import MSPError


@pytest.mark.parametrize("fault", ["no_reply", "bad_checksum", "wrong_command"])
def test_communication_faults_are_detected(make_faulty_fc, fault):
    fc = make_faulty_fc(fault)
    with pytest.raises(MSPError):
        fc.api_version()


def test_noisy_gyro_is_detected(make_faulty_fc):
    fc = make_faulty_fc("noisy_gyro")
    roll_spread, pitch_spread = attitude_spread(fc, delay=0)
    assert roll_spread > 2.0 or pitch_spread > 2.0, "Noisy gyro was NOT detected"