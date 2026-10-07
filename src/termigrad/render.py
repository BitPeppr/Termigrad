import numpy as np

# Constants ---------------------------------------------------------------

GRADIENT = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\\|()1{}[]?-_+~<>i!lI;:,\"^`'."

_LUT = np.frombuffer(GRADIENT.encode("ascii"), dtype=np.uint8)
_TOP = float(_LUT.size - 1)

_ESC_HEAD = b"\x1b[38;2;"                         
_ESC_TAIL = b"m"                                 
_ESC_W = len(_ESC_HEAD) + 11 + len(_ESC_TAIL)   
_CELL = _ESC_W + 1                             
_PALETTE = (
    ( 93,   0,   9), (108,   0,  10), (124,   1,  11), (139,  11,  13),
    (154,  24,  17), (168,  40,  26), (178,  61,  44), (188,  81,  62),
    (197, 101,  82), (205, 120, 101), (212, 140, 124), (218, 160, 147),
    (224, 179, 170), (231, 199, 192), (231, 212, 209), (232, 225, 224),
    (215, 221, 227), (184, 199, 216), (150, 178, 212), (125, 163, 212),
    (102, 148, 210), ( 82, 133, 204), ( 67, 119, 197), ( 55, 107, 192),
    ( 48,  96, 183), ( 41,  85, 173), ( 36,  75, 160), ( 33,  66, 146),
    ( 30,  58, 132), ( 27,  50, 119), ( 24,  43, 106), ( 20,  35,  93),
)

LEVELS = len(_PALETTE)

_ESC_LUT = np.frombuffer(
    b"".join(
        _ESC_HEAD + b"%03d;%03d;%03d" % tuple(rgb) + _ESC_TAIL
        for rgb in _PALETTE[::-1]
    ),
    dtype=np.uint8,
).reshape(LEVELS, _ESC_W)


# Render ------------------------------------------------------------------

def _normalise(array):
    peak = float(array.max())
    if not 0.0 < peak < np.inf:
        array = np.nan_to_num(array, nan=0.0, posinf=1.0, neginf=0.0)
        peak = float(array.max())
        if not 0.0 < peak < np.inf:
            peak = 1.0
    return array / peak


def render(array, colour=True):
    t = _normalise(array)

    chars = _LUT[np.clip((1.0 - t) * _TOP, 0.0, _TOP).astype(np.uint8)]

    if not colour:
        return b"\n".join(row.tobytes() for row in chars) + b"\n"

    level = np.clip(t * (LEVELS - 1) + 0.5, 0.0, LEVELS - 1).astype(np.uint8)

    h, w = chars.shape
    buf = np.empty((h, w * _CELL + 1), dtype=np.uint8)

    cell = buf[:, : w * _CELL].reshape(h, w, _CELL)

    cell[:, :, :_ESC_W] = _ESC_LUT[level]   
    cell[:, :, _ESC_W] = chars             
    buf[:, -1] = 0x0A                     

    return buf.tobytes()
