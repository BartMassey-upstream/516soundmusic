import numpy as np
import os

SAMPLE = 48000
MAX16 = 32767
STANDING_DUR = 3
T = np.int16
T = np.linspace(0, STANDING_DUR, int(SAMPLE * STANDING_DUR), endpoint=False)
E2_FREQ = 82.41  # low E string on guitar
A2_FREQ = 110  # A string on guitar
D3_FREQ = 146.83  # D string on guitar
G3_FREQ = 196  # G string on guitar
B3_FREQ = 246.94  # B string on guitar
E4_FREQ = 329.63  # E string on guitar

NOTES_DICT = {1: "E (Low)", 2: "A", 3: "D", 4: "G", 5: "B", 6: "E (High)"}


def termClear():
    os.system("cls" if os.name == "nt" else "clear")
