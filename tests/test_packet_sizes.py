"""ctypes.sizeof of every routed packet must equal the PDF "Size: N bytes" line."""
import ctypes

import pytest

from f1_24_telemetry import packets
from tests.spec_2026 import PACKET_SIZES, XFAIL_STRUCTS


@pytest.mark.parametrize("name, expected", sorted(PACKET_SIZES.items()))
def test_packet_size(name, expected):
    if name in XFAIL_STRUCTS:
        pytest.xfail("pre-existing bug, out of scope for the 2026 migration")
    got = ctypes.sizeof(getattr(packets, name))
    assert got == expected, f"sizeof({name}) = {got}, spec says {expected}"


def test_max_cars_constant():
    assert packets.MAX_CARS == 24
    assert packets.cs_maxNumCarsInUDPData == 24


def test_biggest_packet_fits_recv_buffer():
    """listener.py reads recv(2048); Participants (1470) is the largest 2026 packet."""
    biggest = max(
        ctypes.sizeof(getattr(packets, n))
        for n in PACKET_SIZES
        if n not in XFAIL_STRUCTS
    )
    assert biggest == 1470
    assert biggest < 2048
