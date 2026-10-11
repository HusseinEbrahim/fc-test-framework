import pytest
from msp_client import MSPClient, MSPError


def test_build_request_api_version():
    assert MSPClient.build_request(1) == bytes([36, 77, 60, 0, 1, 1])


def test_build_request_checksum():
    assert MSPClient.build_request(102)[-1] == 102


def test_parse_valid_reply():
    reply = bytes([36, 77, 62, 3, 1, 0, 1, 46, 45])
    assert MSPClient.parse_reply(reply, 1) == bytes([0, 1, 46])


@pytest.mark.parametrize("name, reply", [
    ("empty",          bytes([])),
    ("wrong header",   bytes([36, 77, 33, 3, 1, 0, 1, 46, 45])),
    ("wrong command",  bytes([36, 77, 62, 3, 2, 0, 1, 46, 46])),
    ("bad checksum",   bytes([36, 77, 62, 3, 1, 0, 1, 47, 45])),
    ("truncated",      bytes([36, 77, 62, 3, 1, 0])),
])
def test_parse_rejects_bad_replies(name, reply):
    with pytest.raises(MSPError):
        MSPClient.parse_reply(reply, 1)