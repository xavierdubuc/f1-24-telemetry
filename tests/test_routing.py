"""HEADER_FIELD_TO_PACKET_TYPE must route exactly the 17 (2026, 1, N) packet ids."""
import ctypes

from f1_24_telemetry import packets
from f1_24_telemetry.packets import HEADER_FIELD_TO_PACKET_TYPE as ROUTE
from tests.spec_2026 import ROUTING


def test_routing_keys_are_exactly_2026_v1_0_to_16():
    assert set(ROUTE) == {(2026, 1, n) for n in range(17)}


def test_no_legacy_format_keys():
    for fmt, _ver, _pid in ROUTE:
        assert fmt == 2026, f"stale routing key for packet_format {fmt}"


def test_routing_targets_match_spec():
    for key, class_name in ROUTING.items():
        assert ROUTE[key] is getattr(packets, class_name)
        assert issubclass(ROUTE[key], packets.Packet)


def test_car_telemetry2_is_id_16():
    assert ROUTE[(2026, 1, 16)] is packets.PacketCarTelemetry2Data


def test_packet_header_format_field():
    fields = dict(packets.PacketHeader._fields_)
    assert fields["packet_format"] is ctypes.c_uint16  # spec: uint16 m_packetFormat // 2026
    assert packets.PacketHeader.packet_format.offset == 0
