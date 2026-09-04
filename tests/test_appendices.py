"""appendices.py must carry the 2026 ID tables and drop the dead tkinter import."""
import pathlib

import pytest

from f1_24_telemetry import appendices
from tests.spec_2026 import APPENDIX_EXPECTATIONS, APPENDIX_PRESERVED_KEYS


def test_no_tkinter_import():
    src = pathlib.Path(appendices.__file__).read_text(encoding="utf-8")
    assert "tkinter" not in src


@pytest.mark.parametrize("attr, key, value", APPENDIX_EXPECTATIONS)
def test_appendix_entry(attr, key, value):
    table = getattr(appendices, attr)
    assert table.get(key) == value


@pytest.mark.parametrize("attr, keys", sorted(APPENDIX_PRESERVED_KEYS.items()))
def test_pre_2026_keys_preserved(attr, keys):
    table = getattr(appendices, attr)
    missing = [k for k in keys if k not in table]
    assert not missing, f"{attr} lost pre-existing keys {missing}"


def test_team_ids_span_465_to_486():
    assert all(k in appendices.TEAM_IDS for k in range(465, 487))


def test_driver_ids_span_186_to_197():
    assert all(k in appendices.DRIVER_IDS for k in range(186, 198))
