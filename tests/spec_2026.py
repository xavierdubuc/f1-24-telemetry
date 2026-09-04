"""Expected packet layout transcribed from the official UDP specification.

Source: "Data Output from F1(R) 25 : 2026 Season Pack" - Version 1.1
        (packet_format 2026). Struct definitions: pages 2-18. ID tables: pages 25-27.

``PDF_LAYOUT`` maps every struct in ``f1_24_telemetry.packets`` to its ordered
field types *as written in the PDF* -- each entry is ``(token, length)`` where
``length == 0`` means a scalar and ``length > 0`` a fixed array.  ``token`` is a
primitive name (see ``TYPE_TOKENS``) or the name of another struct class.

Field *names* are the library's own snake_case; only the ordering, the C types,
the array lengths and the total ``Size: N bytes`` come from the PDF.  The
compliance tests recompute every field offset assuming ``_pack_ = 1`` (the spec
guarantees "all data is packed, there is no padding used").

Two structs are known to be broken in a way that predates the 2026 migration and
is explicitly out of scope for it (see ``XFAIL_STRUCTS``):
  * ``PacketMotionExData`` - three wheel arrays declared as scalars (-36 bytes),
  * ``PacketLapPositionsData`` - ``_fields`` typo, so ctypes registers no fields.
"""

TYPE_TOKENS = {
    "uint8": "c_uint8",
    "int8": "c_int8",
    "uint16": "c_uint16",
    "int16": "c_int16",
    "uint32": "c_uint32",
    "uint64": "c_uint64",
    "float": "c_float",
    "double": "c_double",
    "char": "c_char",
}

# Primitive byte sizes, used to recompute offsets independently of ctypes.
TOKEN_SIZE = {
    "c_uint8": 1, "c_int8": 1,
    "c_uint16": 2, "c_int16": 2,
    "c_uint32": 4, "c_float": 4,
    "c_uint64": 8, "c_double": 8,
    "c_char": 1,
}

U8, I8 = ("uint8", 0), ("int8", 0)
U16, I16 = ("uint16", 0), ("int16", 0)
U32, U64 = ("uint32", 0), ("uint64", 0)
F32, F64 = ("float", 0), ("double", 0)


def _rep(tok, n):
    return [tok] * n


PDF_LAYOUT = {
    # ---- Header (p.2) ----
    "PacketHeader": [
        U16, U8, U8, U8, U8, U8, U64, F32, U32, U32, U8, U8,
    ],
    # ---- Motion (p.3), Size 1325 ----
    "CarMotionData": [
        F32, F32, F32, F32, F32, F32,          # world position + velocity
        I16, I16, I16, I16, I16, I16,           # world forward / right dir (normalised)
        I16, I16, I16,                          # g-force lateral / longitudinal / vertical (quantised)
        F32, F32, F32,                          # yaw / pitch / roll
    ],
    "PacketMotionData": [("PacketHeader", 0), ("CarMotionData", 24)],
    # ---- Session (p.4-5), Size 926 ----
    "MarshalZone": [F32, I8],
    "ActiveAeroZone": [F32, F32],
    "DRSZone": [F32, F32],
    "WeatherForecastSample": [U8, U8, U8, I8, I8, I8, I8, U8],
    "PacketSessionData": [
        ("PacketHeader", 0),
        U8, I8, I8, U8, U16, U8, I8, U8, U16, U16, U8, U8, U8, U8, U8, U8,
        ("MarshalZone", 21),
        U8, U8, U8,
        ("WeatherForecastSample", 64),
        U8, U8, U32, U32, U32, U8, U8, U8,
        U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U32,
        U8, U8, U8, U8, U8, U8, U8, U8,
        U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8,
        U8, U8, U8, U8, U8, U8,
        (("uint8"), 12),                        # weekend_structure[12]
        F32, F32,                               # sector2 / sector3 lap distance start
        # --- 2026 Season Pack additions ---
        U8, U8, ("ActiveAeroZone", 8), U8, ("ActiveAeroZone", 8), U8, ("DRSZone", 4),
        F32, U8, U8, U8, U8, U8,
    ],
    # ---- Lap Data (p.6), Size 1399 ----
    "LapData": [
        U32, U32, U16, U8, U16, U8, U16, U8, U16, U8,
        F32, F32, F32,
        U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8, U8,
        U16, U16, U8, F32, U8,
    ],
    "PacketLapData": [("PacketHeader", 0), ("LapData", 24), U8, U8],
    # ---- Event (p.7-9), Size 45 ----
    "FastestLap": [U8, F32],
    "Retirement": [U8, U8],
    "DRSDisabled": [U8],
    "TeamMateInPits": [U8],
    "RaceWinner": [U8],
    "Penalty": [U8, U8, U8, U8, U8, U8, U8],
    "SpeedTrap": [U8, F32, U8, U8, U8, F32],
    "StartLights": [U8],
    "DriveThroughPenaltyServed": [U8],
    "StopGoPenaltyServed": [U8, F32],
    "Flashback": [U32, F32],
    "Buttons": [U32],
    "OverTake": [U8, U8],
    "SafetyCar": [U8, U8],
    "Collision": [U8, U8, U8],                  # + severity (2026)
    "PacketEventData": [("PacketHeader", 0), (("uint8"), 4), ("EventDataDetails", 0)],
    # ---- Participants (p.9), Size 1470 ----
    "Color": [U8, U8, U8],                      # LiveryColour in the PDF
    "ParticipantData": [
        U8, U16, U16, U16,                      # ai, driver_id, network_id, team_id (u16 since 2026)
        U8, U8, U8, ("char", 32),
        U8, U8, U16, U8, U8, ("Color", 4),
    ],
    "PacketParticipantsData": [("PacketHeader", 0), U8, ("ParticipantData", 24)],
    # ---- Car Setups (p.10), Size 1233 ----
    "CarSetupData": [
        U8, U8, U8, U8,
        F32, F32, F32, F32,
        U8, U8, U8, U8, U8, U8, U8, U8, U8,
        F32, F32, F32, F32,
        U8, F32,
    ],
    "PacketCarSetupData": [("PacketHeader", 0), ("CarSetupData", 24), F32],
    # ---- Car Telemetry (p.10-11), Size 1448 ----
    "CarTelemetryData": [
        U16, F32, F32, F32, U8, I8, U16, U8, U8, U16,
        (("uint16"), 4),                        # brakes_temperature[4]
        (("uint8"), 4),                         # tyres_surface_temperature[4]
        (("uint8"), 4),                         # tyres_inner_temperature[4]
        U8,                                     # engine_temperature (u8 since 2026)
        (("float"), 4),                         # tyres_pressure[4]
        (("uint8"), 4),                         # surface_type[4]
    ],
    "PacketCarTelemetryData": [("PacketHeader", 0), ("CarTelemetryData", 24), U8, U8, I8],
    # ---- Car Status (p.11-12), Size 1445 ----
    "CarStatusData": [
        U8, U8, U8, U8, U8,
        F32, F32, F32,
        U16, U16, U8, U8, U16,
        U8, U8, U8, I8,
        F32, F32, F32,
        U8,
        F32, F32, F32, F32,                     # mguk, mguh, HARVEST LIMIT PER LAP (2026), deployed
        U8,
    ],
    "PacketCarStatusData": [("PacketHeader", 0), ("CarStatusData", 24)],
    # ---- Final Classification (p.12), Size 1134 ----
    "FinalClassificationData": [
        U8, U8, U8, U8, U8, U8, U8,
        U32, F64, U8, U8, U8,
        (("uint8"), 8), (("uint8"), 8), (("uint8"), 8),
    ],
    "PacketFinalClassificationData": [
        ("PacketHeader", 0), U8, ("FinalClassificationData", 24),
    ],
    # ---- Lobby Info (p.13), Size 1062 ----
    "LobbyInfoData": [
        U8, U16, U8, U8, ("char", 32), U8, U8, U8, U16, U8,
    ],
    "PacketLobbyInfoData": [("PacketHeader", 0), U8, ("LobbyInfoData", 24)],
    # ---- Car Damage (p.13-14), Size 1133 ----
    "CarDamageData": [
        (("float"), 4),                         # tyres_wear[4]
        (("uint8"), 4), (("uint8"), 4), (("uint8"), 4),
    ] + _rep(U8, 18),
    "PacketCarDamageData": [("PacketHeader", 0), ("CarDamageData", 24)],
    # ---- Session History (p.14), Size 1460 ----
    "LapHistoryData": [U32, U16, U8, U16, U8, U16, U8, U8],
    "TyreStintHistoryData": [U8, U8, U8],
    "PacketSessionHistoryData": [
        ("PacketHeader", 0), U8, U8, U8, U8, U8, U8, U8,
        ("LapHistoryData", 100), ("TyreStintHistoryData", 8),
    ],
    # ---- Tyre Sets (p.15), Size 231 ----
    "TyreSetData": [U8, U8, U8, U8, U8, U8, U8, I16, U8],
    "PacketTyreSetsData": [("PacketHeader", 0), U8, ("TyreSetData", 20), U8],
    # ---- Motion Ex (p.16), Size 273  [XFAIL: wheel arrays declared scalar] ----
    "PacketMotionExData": [
        ("PacketHeader", 0),
        (("float"), 4), (("float"), 4), (("float"), 4), (("float"), 4),
        (("float"), 4), (("float"), 4), (("float"), 4), (("float"), 4),
        F32, F32, F32, F32, F32, F32, F32, F32, F32, F32,
        F32,
        (("float"), 4),                         # m_wheelVertForce[4]
        F32, F32, F32, F32, F32, F32,
        (("float"), 4), (("float"), 4),         # m_wheelCamber[4], m_wheelCamberGain[4]
    ],
    # ---- Time Trial (p.16-17), Size 104 ----
    "TimeTrialDataSet": [
        U8, U16, U32, U32, U32, U32, U8, U8, U8, U8, U8, U8,
    ],
    "PacketTimeTrialData": [
        ("PacketHeader", 0),
        ("TimeTrialDataSet", 0), ("TimeTrialDataSet", 0), ("TimeTrialDataSet", 0),
    ],
    # ---- Lap Positions (p.17), Size 1231  [XFAIL: `_fields` typo] ----
    "PacketLapPositionsData": [
        ("PacketHeader", 0), U8, U8, (("uint8"), 50 * 24),
    ],
    # ---- Car Telemetry 2 (p.17-18), Size 269 -- NEW in 2026 ----
    "CarTelemetry2Data": [U8, U8, U16, U8, U8, U16, U8, U8],
    "PacketCarTelemetry2Data": [("PacketHeader", 0), ("CarTelemetry2Data", 24)],
}


# "Size: N bytes" lines from the PDF, one per routed packet.
PACKET_SIZES = {
    "PacketMotionData": 1325,
    "PacketSessionData": 926,
    "PacketLapData": 1399,
    "PacketEventData": 45,
    "PacketParticipantsData": 1470,
    "PacketCarSetupData": 1233,
    "PacketCarTelemetryData": 1448,
    "PacketCarStatusData": 1445,
    "PacketFinalClassificationData": 1134,
    "PacketLobbyInfoData": 1062,
    "PacketCarDamageData": 1133,
    "PacketSessionHistoryData": 1460,
    "PacketTyreSetsData": 231,
    "PacketMotionExData": 273,
    "PacketTimeTrialData": 104,
    "PacketLapPositionsData": 1231,
    "PacketCarTelemetry2Data": 269,
}

# Sub-struct sizes derived from the PDF field lists (independent cross-check).
SUBSTRUCT_SIZES = {
    "PacketHeader": 29,
    "CarMotionData": 54,
    "MarshalZone": 5,
    "ActiveAeroZone": 8,
    "DRSZone": 8,
    "WeatherForecastSample": 8,
    "LapData": 57,
    "Penalty": 7,
    "SpeedTrap": 12,
    "EventDataDetails": 12,
    "Color": 3,
    "ParticipantData": 60,
    "CarSetupData": 50,
    "CarTelemetryData": 59,
    "CarStatusData": 59,
    "FinalClassificationData": 46,
    "LobbyInfoData": 43,
    "CarDamageData": 46,
    "LapHistoryData": 14,
    "TyreStintHistoryData": 3,
    "TyreSetData": 10,
    "TimeTrialDataSet": 25,
    "CarTelemetry2Data": 10,
}

# Packet id -> class name, from "Packet IDs" (p.2-3), for packet_format 2026 / version 1.
ROUTING = {
    (2026, 1, 0): "PacketMotionData",
    (2026, 1, 1): "PacketSessionData",
    (2026, 1, 2): "PacketLapData",
    (2026, 1, 3): "PacketEventData",
    (2026, 1, 4): "PacketParticipantsData",
    (2026, 1, 5): "PacketCarSetupData",
    (2026, 1, 6): "PacketCarTelemetryData",
    (2026, 1, 7): "PacketCarStatusData",
    (2026, 1, 8): "PacketFinalClassificationData",
    (2026, 1, 9): "PacketLobbyInfoData",
    (2026, 1, 10): "PacketCarDamageData",
    (2026, 1, 11): "PacketSessionHistoryData",
    (2026, 1, 12): "PacketTyreSetsData",
    (2026, 1, 13): "PacketMotionExData",
    (2026, 1, 14): "PacketTimeTrialData",
    (2026, 1, 15): "PacketLapPositionsData",
    (2026, 1, 16): "PacketCarTelemetry2Data",
}

# Broken before the 2026 migration, left untouched by chantier 14 (see module docstring).
XFAIL_STRUCTS = {"PacketMotionExData", "PacketLapPositionsData"}

# Union members that must all be present in EventDataDetails (p.7-8).
EVENT_UNION_MEMBERS = {
    "fastest_lap", "retirement", "drs_disabled", "team_mate_in_pits", "race_winner",
    "penalty", "speed_trap", "start_lights", "drive_through_penalty_served",
    "stop_go_penalty_served", "flashback", "buttons", "overtake", "safety_car",
    "collision",
}

# Appendix expectations (pages 25-27). ``(module_attr, key, value)``.
APPENDIX_EXPECTATIONS = [
    # Team IDs (p.25) - 2026 additions
    ("TEAM_IDS", 465, "Art GP ‘25"),
    ("TEAM_IDS", 466, "Campos ‘25"),
    ("TEAM_IDS", 467, "Rodin Motorsport ‘25"),
    ("TEAM_IDS", 468, "AIX Racing ‘25"),
    ("TEAM_IDS", 469, "DAMS ‘25"),
    ("TEAM_IDS", 470, "Hitech ‘25"),
    ("TEAM_IDS", 471, "MP Motorsport ‘25"),
    ("TEAM_IDS", 472, "Prema ‘25"),
    ("TEAM_IDS", 473, "Trident ‘25"),
    ("TEAM_IDS", 474, "Van Amersfoort Racing ‘25"),
    ("TEAM_IDS", 475, "Invicta ‘25"),
    ("TEAM_IDS", 476, "Mercedes ‘26"),
    ("TEAM_IDS", 477, "Ferrari ‘26"),
    ("TEAM_IDS", 478, "Red Bull Racing ‘26"),
    ("TEAM_IDS", 479, "Williams ‘26"),
    ("TEAM_IDS", 480, "Aston Martin ‘26"),
    ("TEAM_IDS", 481, "Alpine ‘26"),
    ("TEAM_IDS", 482, "RB ‘26"),
    ("TEAM_IDS", 483, "Haas ‘26"),
    ("TEAM_IDS", 484, "McLaren ‘26"),
    ("TEAM_IDS", 485, "Audi ‘26"),
    ("TEAM_IDS", 486, "Cadillac ‘26"),
    # Driver IDs (p.26)
    ("DRIVER_IDS", 10, "Nico Hülkenberg"),
    ("DRIVER_IDS", 185, "Luca Cortez"),
    ("DRIVER_IDS", 186, "Luke Browning"),
    ("DRIVER_IDS", 187, "Cian Shields"),
    ("DRIVER_IDS", 188, "Arvid Lindblad"),
    ("DRIVER_IDS", 189, "Dino Beganovic"),
    ("DRIVER_IDS", 190, "Leonardo Fornaroli"),
    ("DRIVER_IDS", 191, "Oliver Goethe"),
    ("DRIVER_IDS", 192, "Gabriele Minì"),
    ("DRIVER_IDS", 193, "Sebastián Montoya"),
    ("DRIVER_IDS", 194, "Alexander Dunne"),
    ("DRIVER_IDS", 195, "Max Esterson"),
    ("DRIVER_IDS", 196, "Sami Meguetounif"),
    ("DRIVER_IDS", 197, "John Bennett"),
    # Track IDs (p.27)
    ("TRACK_IDS", 42, "Madrid"),
    # Formula / ERS deploy mode
    ("FORMULA", 13, "F1 26"),
    ("ERS_DEPLOYMENT_MODE", 3, "Boost"),
]

# Keys that existed before chantier 14 and must not regress.
APPENDIX_PRESERVED_KEYS = {
    "TEAM_IDS": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194],
    "DRIVER_IDS": [0, 9, 50, 54, 58, 147, 165, 175],
    "TRACK_IDS": [0, 10, 26, 41],
}
