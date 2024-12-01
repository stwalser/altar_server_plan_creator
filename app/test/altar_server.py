import pytest

from altar_servers.altar_server import AltarServer
from utils.utils import load_yaml_file


@pytest.fixture(scope='session')
def raw_altar_servers():
    raw_altar_servers = load_yaml_file("altar_servers_test.yaml")
    yield raw_altar_servers

class TestAltarServer:
    def test_name(self, raw_altar_servers):
        for raw_altar_server in raw_altar_servers:
            altar_server = AltarServer(raw_altar_server)
            raw_name = list(raw_altar_server.keys())[0]
            assert altar_server.name == raw_name

    def test_avoid(self, raw_altar_servers):
        for raw_altar_server in raw_altar_servers:
            altar_server = AltarServer(raw_altar_server)
            attributes = list(raw_altar_server.values())[0]
            if "avoid" in attributes:
                assert altar_server.avoid == attributes["avoid"]

    def test_vacation(self, raw_altar_servers):
        for raw_altar_server in raw_altar_servers:
            altar_server = AltarServer(raw_altar_server)
            attributes = list(raw_altar_server.values())[0]
            if "vacation" in attributes:
                assert altar_server.vacations == attributes["vacation"]
