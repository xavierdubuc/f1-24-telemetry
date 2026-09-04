"""Helpers to compare a ctypes struct against a PDF_LAYOUT entry."""
import ctypes

from f1_24_telemetry import packets

from tests.spec_2026 import TOKEN_SIZE, TYPE_TOKENS


def resolve_token(token):
    """Return (ctype_or_class, byte_size) for a PDF_LAYOUT token."""
    if token in TYPE_TOKENS:
        ct = getattr(ctypes, TYPE_TOKENS[token])
        return ct, TOKEN_SIZE[TYPE_TOKENS[token]]
    cls = getattr(packets, token)
    return cls, ctypes.sizeof(cls)


def field_base_and_length(ftype):
    """Split a ctypes _fields_ entry type into (base_type, array_length)."""
    if hasattr(ftype, "_length_") and hasattr(ftype, "_type_"):
        return ftype._type_, ftype._length_
    return ftype, 0


def walk(struct_name, spec):
    """Yield dicts describing each expected vs actual field, plus recompute offsets.

    Raises AssertionError with a precise message on the first divergence.
    """
    cls = getattr(packets, struct_name)
    fields = cls._fields_
    assert len(fields) == len(spec), (
        f"{struct_name}: expected {len(spec)} fields per spec, got {len(fields)}"
    )

    offset = 0
    for i, ((fname, ftype), (token, length)) in enumerate(zip(fields, spec)):
        exp_base, exp_base_size = resolve_token(token)
        got_base, got_length = field_base_and_length(ftype)

        assert got_length == length, (
            f"{struct_name}.{fname} (field {i}): expected array length {length}, "
            f"got {got_length}"
        )
        assert got_base == exp_base, (
            f"{struct_name}.{fname} (field {i}): expected base type {exp_base}, "
            f"got {got_base}"
        )

        actual_offset = getattr(cls, fname).offset
        assert actual_offset == offset, (
            f"{struct_name}.{fname} (field {i}): expected offset {offset} "
            f"(packed, no padding), got {actual_offset}"
        )
        offset += exp_base_size * max(length, 1)

    assert offset == ctypes.sizeof(cls), (
        f"{struct_name}: sum of field sizes {offset} != ctypes.sizeof {ctypes.sizeof(cls)}"
    )
    return offset
