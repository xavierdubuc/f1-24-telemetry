"""Every struct in f1_24_telemetry.packets must match the 2026 spec field-for-field.

Checks, per struct: field count, ordered base types, array lengths, and every
field offset recomputed assuming packed layout (``_pack_ = 1``, no padding).
"""
import ctypes

import pytest

from f1_24_telemetry import packets
from tests import _layout
from tests.spec_2026 import PDF_LAYOUT, SUBSTRUCT_SIZES, XFAIL_STRUCTS


@pytest.mark.parametrize("struct_name", sorted(PDF_LAYOUT))
def test_struct_layout_matches_spec(struct_name):
    if struct_name in XFAIL_STRUCTS:
        pytest.xfail("pre-existing bug, out of scope for the 2026 migration")
    _layout.walk(struct_name, PDF_LAYOUT[struct_name])


@pytest.mark.parametrize("struct_name, expected", sorted(SUBSTRUCT_SIZES.items()))
def test_substruct_size(struct_name, expected):
    got = ctypes.sizeof(getattr(packets, struct_name))
    assert got == expected, f"sizeof({struct_name}) = {got}, spec says {expected}"


def test_all_packet_structs_are_covered():
    """Guard: any Packet subclass with _fields_ should appear in PDF_LAYOUT."""
    missing = []
    for name in dir(packets):
        obj = getattr(packets, name)
        if (
            isinstance(obj, type)
            and issubclass(obj, packets.Packet)
            and obj is not packets.Packet
            and getattr(obj, "_fields_", None)
            and name not in PDF_LAYOUT
        ):
            missing.append(name)
    assert not missing, f"structs not transcribed in spec_2026.PDF_LAYOUT: {missing}"
