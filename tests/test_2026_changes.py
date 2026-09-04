"""Targeted checks for each field/struct change introduced by the 2026 Season Pack."""
import ctypes

from f1_24_telemetry import packets
from tests.spec_2026 import EVENT_UNION_MEMBERS


def _types(cls):
    return dict(cls._fields_)


def _names(cls):
    return [n for n, _ in cls._fields_]


# --- 14b: 24 cars everywhere ---------------------------------------------------

def test_per_car_arrays_are_24():
    expect = {
        "PacketMotionData": "car_motion_data",
        "PacketLapData": "lap_data",
        "PacketParticipantsData": "participants",
        "PacketCarSetupData": "car_setups",
        "PacketCarTelemetryData": "car_telemetry_data",
        "PacketCarStatusData": "car_status_data",
        "PacketFinalClassificationData": "classification_data",
        "PacketLobbyInfoData": "lobby_players",
        "PacketCarDamageData": "car_damage_data",
        "PacketCarTelemetry2Data": "car_telemetry2_data",
    }
    for cls_name, field in expect.items():
        ftype = _types(getattr(packets, cls_name))[field]
        assert ftype._length_ == 24, f"{cls_name}.{field} array length {ftype._length_}"


# --- 14c: motion G-forces float -> int16 ------------------------------------

def test_gforces_are_int16():
    t = _types(packets.CarMotionData)
    for f in ("g_force_lateral", "g_force_longitudinal", "g_force_vertical"):
        assert t[f] is ctypes.c_int16


# --- 14d: session weather samples 56 -> 64, aero/DRS zones, assists ---------

def test_weather_forecast_samples_is_64():
    t = _types(packets.PacketSessionData)
    assert t["weather_forecast_samples"]._length_ == 64
    assert t["weather_forecast_samples"]._type_ is packets.WeatherForecastSample


def test_active_aero_and_drs_zone_structs():
    for cls in (packets.ActiveAeroZone, packets.DRSZone):
        assert [n for n, _ in cls._fields_] == ["zone_start", "zone_end"]
        assert all(ft is ctypes.c_float for _, ft in cls._fields_)
        assert ctypes.sizeof(cls) == 8


def test_session_2026_tail_fields_present_and_ordered():
    names = _names(packets.PacketSessionData)
    tail = [
        "active_aero_track_status",
        "num_active_aero_zones_full",
        "active_aero_zones_full",
        "num_active_aero_zones_partial",
        "active_aero_zones_partial",
        "num_drs_zones",
        "drs_zones",
        "start_reaction_time",
        "anti_lock_brakes_assist",
        "traction_control_assist",
        "dynamic_racing_line_hi_vis",
        "dynamic_racing_line_colour_blind",
        "recurring_rewind_prompt",
    ]
    assert names[-len(tail):] == tail
    t = _types(packets.PacketSessionData)
    assert t["active_aero_zones_full"]._type_ is packets.ActiveAeroZone
    assert t["active_aero_zones_full"]._length_ == 8
    assert t["active_aero_zones_partial"]._length_ == 8
    assert t["drs_zones"]._type_ is packets.DRSZone
    assert t["drs_zones"]._length_ == 4
    assert t["start_reaction_time"] is ctypes.c_float


# --- 14e: participants driver/network/team id uint8 -> uint16 ---------------

def test_participant_ids_are_uint16():
    t = _types(packets.ParticipantData)
    for f in ("driver_id", "network_id", "team_id"):
        assert t[f] is ctypes.c_uint16


# --- 14f: car telemetry engine_temperature uint16 -> uint8 -----------------

def test_engine_temperature_is_uint8():
    t = _types(packets.CarTelemetryData)
    assert t["engine_temperature"] is ctypes.c_uint8
    # the fields after it must not have shifted
    assert t["tyres_pressure"]._type_ is ctypes.c_float
    assert t["tyres_pressure"]._length_ == 4
    assert t["surface_type"]._length_ == 4


# --- 14g: car status ers_harvested_limit_per_lap inserted ------------------

def test_ers_harvest_limit_position():
    names = _names(packets.CarStatusData)
    i = names.index("ers_harvested_limit_per_lap")
    assert names[i - 1] == "ers_harvested_this_lap_mguh"
    assert names[i + 1] == "ers_deployed_this_lap"
    assert _types(packets.CarStatusData)["ers_harvested_limit_per_lap"] is ctypes.c_float


# --- 14h: collision severity ---------------------------------------------------

def test_collision_severity_and_event_union_unchanged_size():
    names = _names(packets.Collision)
    assert names == ["vehicle1_idx", "vehicle2_idx", "severity"]
    assert _types(packets.Collision)["severity"] is ctypes.c_uint8
    assert ctypes.sizeof(packets.Collision) == 3
    assert ctypes.sizeof(packets.EventDataDetails) == 12  # sized by SpeedTrap
    assert ctypes.sizeof(packets.PacketEventData) == 45
    assert set(_names(packets.EventDataDetails)) == EVENT_UNION_MEMBERS


# --- 14i / 14j: lobby & time trial team_id uint8 -> uint16 -----------------

def test_lobby_and_timetrial_team_id_are_uint16():
    assert _types(packets.LobbyInfoData)["team_id"] is ctypes.c_uint16
    assert _types(packets.TimeTrialDataSet)["team_id"] is ctypes.c_uint16


# --- 14j-bis: trivial spec fixes pulled in by the layout tests -------------

def test_tyreset_lap_delta_time_is_signed():
    assert _types(packets.TyreSetData)["lap_delta_time"] is ctypes.c_int16


def test_lap_history_data_has_distinct_sector_minute_fields():
    names = _names(packets.LapHistoryData)
    assert names.count("sector1_time_minutes") == 1
    assert "sector3_time_minutes" in names


# --- 14k: Car Telemetry 2 packet --------------------------------------------

def test_car_telemetry2_struct():
    expected = [
        ("active_aero_mode", ctypes.c_uint8),
        ("active_aero_available", ctypes.c_uint8),
        ("active_aero_activation_distance", ctypes.c_uint16),
        ("overtake_available", ctypes.c_uint8),
        ("overtake_active", ctypes.c_uint8),
        ("overtake_activation_distance", ctypes.c_uint16),
        ("regulations_2026", ctypes.c_uint8),
        ("driving_wrong_way", ctypes.c_uint8),
    ]
    assert list(packets.CarTelemetry2Data._fields_) == expected
    assert ctypes.sizeof(packets.CarTelemetry2Data) == 10
    assert ctypes.sizeof(packets.PacketCarTelemetry2Data) == 269
