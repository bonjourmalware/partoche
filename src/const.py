import os
from math import ceil

UTM_Y_AXIS = [
    "X",
    "W",
    "V",
    "U",
    "T",
    "S",
    "R",
    "Q",
    "P",
    "N",
    "M",
    "L",
    "K",
    "J",
    "H",
    "G",
    "F",
    "E",
    "D",
    "C",
]

UTM_X_AXIS = [
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35,
    36,
    37,
    38,
    39,
    40,
    41,
    42,
    43,
    44,
    45,
    46,
    47,
    48,
    49,
    50,
    51,
    52,
    53,
    54,
    55,
    56,
    57,
    58,
    59,
    60,
]

COLS, LINES = os.get_terminal_size()

X_COEFF = float(COLS) / len(UTM_X_AXIS)
Y_COEFF = float(LINES) / len(UTM_Y_AXIS)

TILE_W, TILE_H = ceil(X_COEFF), ceil(Y_COEFF)
TIMERANGE_PLACEHOLDER = "!!TIMERANGE!!"