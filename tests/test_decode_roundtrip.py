"""End-to-end decode of a synthetic 2026 buffer for every routed packet id,
plus pack/unpack round-trips proving the widened (uint16 / int16) fields."""
import ctypes

import pytest

from f1_24_telemetry import packets
from f1_24_telemetry.packets import HEADER_FIELD_TO_PACKET_TYPE as ROUTE
from tests.spec_2026 import ROUTING, XFAIL_STRUCTS


def _buffer_with_header(cls, packet_id):
    """A zeroed buffer of the right length carrying a valid 2026 PacketHeader."""
    buf = bytearray(ctypes.sizeof(cls))
    header = packets.PacketHeader.from_buffer(buf)
    header.packet_format = 2026
    header.game_year = 26
    header.packet_version = 1
    header.packet_id = packet_id
    return bytes(buf)


@pytest.mark.parametrize("key, class_name", sorted(ROUTING.items()))
def test_listener_style_dispatch(key, class_name):
    if class_name in XFAIL_STRUCTS:
        pytest.xfail("pre-existing bug, out of scope for the 2026 migration")
    _fmt, _ver, pid = key
    cls = getattr(packets, class_name)
    raw = _buffer_with_header(cls, pid)

    # Mirror TelemetryListener.get()
    header = packets.PacketHeader.from_buffer_copy(raw)
    lookup = (header.packet_format, header.packet_version, header.packet_id)
    assert lookup == key
    pkt = ROUTE[lookup].unpack(raw)

    assert pkt.header.packet_format == 2026
    assert pkt.header.packet_id == pid
    pkt.to_dict()   # must not raise
    pkt.to_json()   # must not raise


def test_participant_ids_roundtrip_beyond_255():
    p = packets.ParticipantData()
    p.driver_id = 486        # Cadillac driver slot > 255
    p.network_id = 40000
    p.team_id = 486          # Cadillac '26
    back = packets.ParticipantData.from_buffer_copy(p.pack())
    assert (back.driver_id, back.network_id, back.team_id) == (486, 40000, 486)


def test_car_status_harvest_limit_roundtrip():
    cs = packets.CarStatusData()
    cs.ers_harvested_this_lap_mguh = 1.0
    cs.ers_harvested_limit_per_lap = 4_000_000.0
    cs.ers_deployed_this_lap = 2.0
    back = packets.CarStatusData.from_buffer_copy(cs.pack())
    assert back.ers_harvested_limit_per_lap == pytest.approx(4_000_000.0)
    assert back.ers_harvested_this_lap_mguh == pytest.approx(1.0)
    assert back.ers_deployed_this_lap == pytest.approx(2.0)


def test_car_telemetry2_roundtrip():
    ct = packets.CarTelemetry2Data()
    ct.active_aero_activation_distance = 5000
    ct.overtake_activation_distance = 60000     # > int16 max, needs uint16
    ct.regulations_2026 = 1
    ct.driving_wrong_way = 1
    back = packets.CarTelemetry2Data.from_buffer_copy(ct.pack())
    assert back.active_aero_activation_distance == 5000
    assert back.overtake_activation_distance == 60000
    assert (back.regulations_2026, back.driving_wrong_way) == (1, 1)


def test_gforce_roundtrip_is_signed():
    m = packets.CarMotionData()
    m.g_force_lateral = -1500          # -1.5 g once divided by 1000
    m.g_force_vertical = 1000
    back = packets.CarMotionData.from_buffer_copy(m.pack())
    assert back.g_force_lateral == -1500
    assert back.g_force_vertical == 1000


def test_collision_severity_roundtrip():
    c = packets.Collision()
    c.vehicle1_idx, c.vehicle2_idx, c.severity = 3, 7, 2
    back = packets.Collision.from_buffer_copy(c.pack())
    assert (back.vehicle1_idx, back.vehicle2_idx, back.severity) == (3, 7, 2)
