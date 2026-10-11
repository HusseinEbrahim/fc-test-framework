import pytest
from msp_client import MSPClient, open_real_board
from simulator import SimulatedFC


def pytest_addoption(parser):
    parser.addoption("--hardware", action="store_true", help="Test a real flight controller")
    parser.addoption("--port", default=None, help="Serial port (auto-detected if omitted)")


@pytest.fixture(scope="session")
def fc(request):
    """The device under test: the real board with --hardware, otherwise the simulator."""
    if request.config.getoption("--hardware"):
        client = open_real_board(request.config.getoption("--port"))
    else:
        client = MSPClient(SimulatedFC())
    yield client
    client.close()


@pytest.fixture
def make_faulty_fc():
    """Builds a simulated board that misbehaves in a chosen way."""
    def make(fault):
        return MSPClient(SimulatedFC(fault=fault))
    return make