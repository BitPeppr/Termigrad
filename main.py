import shutil
import sys
import time

import numpy as np

from render import render

# Constants ---------------------------------------------------------------

dim = shutil.get_terminal_size()
shape = (dim.lines, dim.columns)

# F, k, dU, dV = 0.0400, 0.0600, 0.160, 0.080

sims_per_frame = 16

ENTER = b"\x1b[?1049h\x1b[?25l"
FRAME = b"\x1b[H\x1b[2J"
LEAVE = b"\x1b[?25h\x1b[?1049l"

TTY = sys.stdout.isatty()
out = sys.stdout.buffer
FRAME_INTERVAL = 1.0 / 30


# Setup -------------------------------------------------------------------

u = np.ones(shape, dtype=np.float32)
v = np.zeros(shape, dtype=np.float32)

v[dim.lines // 2 - 10 : dim.lines // 2 + 10, dim.columns // 2 - 10 : dim.columns // 2 + 10] = 1.0



_PAD = np.empty((dim.lines + 2, dim.columns + 2), dtype=np.float32)
_LU = np.empty(shape, dtype=np.float32)
_LV = np.empty(shape, dtype=np.float32)


def laplacian(a, out):
    _PAD[1:-1, 1:-1] = a
    _PAD[0, 1:-1] = a[-1]
    _PAD[-1, 1:-1] = a[0]
    _PAD[1:-1, 0] = a[:, -1]
    _PAD[1:-1, -1] = a[:, 0]

    core = _PAD[1:-1, 1:-1]
    np.add(_PAD[:-2, 1:-1], _PAD[2:, 1:-1], out=out)
    out += _PAD[1:-1, :-2]
    out += _PAD[1:-1, 2:]
    out -= 4 * core
    return out



# Simulation loop ---------------------------------------------------------

if TTY:
    out.write(ENTER)
    out.flush()

deadline = time.perf_counter()

try:
    while True:
        for _ in range(sims_per_frame):

            reaction = u * v * v

            lap_u = laplacian(u, _LU)
            lap_v = laplacian(v, _LV)

            u += dU * lap_u - reaction + F * (1 - u)
            v += dV * lap_v + reaction - (F + k) * v

        frame = render(v)
        out.write(FRAME + frame if TTY else frame)
        out.flush()

        if TTY:
            deadline += FRAME_INTERVAL
            delay = deadline - time.perf_counter()
            if delay > 0.0:
                time.sleep(delay)
            else:
                deadline = time.perf_counter()

except (KeyboardInterrupt, BrokenPipeError):
    pass

finally:
    if TTY:
        out.write(LEAVE)
        out.flush()

