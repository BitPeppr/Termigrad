import argparse
import os
import shutil
import sys
import time

import numpy as np

from termigrad import __version__
from termigrad.render import render

# Presets ------------------------------------------------------------------

PRESETS = {
    "spots": (0.0367, 0.0649),
    "coral": (0.0545, 0.0620),
    "worms": (0.0300, 0.0620),
    "stripes": (0.0220, 0.0510),
    "mooncake": (0.0400, 0.0600),
}

DEFAULT_PRESET = "stripes"

DU, DV = 0.160, 0.080

# Simulation ---------------------------------------------------------------

SIMS_PER_FRAME = 16
FRAME_INTERVAL = 1.0 / 30
SEED_RADIUS = 10

MIN_LINES, MIN_COLUMNS = 24, 60


ENTER = b"\x1b[?1049h\x1b[?25l"
FRAME = b"\x1b[H\x1b[2J"
LEAVE = b"\x1b[?25h\x1b[?1049l"


# Field --------------------------------------------------------------------


class Field:

    def __init__(self, shape):
        rows, columns = shape

        self.u = np.ones(shape, dtype=np.float32)
        self.v = np.zeros(shape, dtype=np.float32)

        mid_r, mid_c = rows // 2, columns // 2
        rows_slice = slice(mid_r - SEED_RADIUS, mid_r + SEED_RADIUS)
        columns_slice = slice(mid_c - SEED_RADIUS, mid_c + SEED_RADIUS)
        self.v[rows_slice, columns_slice] = 1.0

        self._pad = np.empty((rows + 2, columns + 2), dtype=np.float32)
        self._lap_u = np.empty(shape, dtype=np.float32)
        self._lap_v = np.empty(shape, dtype=np.float32)

    def _laplacian(self, a, out):
        pad = self._pad
        pad[1:-1, 1:-1] = a
        pad[0, 1:-1] = a[-1]
        pad[-1, 1:-1] = a[0]
        pad[1:-1, 0] = a[:, -1]
        pad[1:-1, -1] = a[:, 0]

        core = pad[1:-1, 1:-1]
        np.add(pad[:-2, 1:-1], pad[2:, 1:-1], out=out)
        out += pad[1:-1, :-2]
        out += pad[1:-1, 2:]
        out -= 4 * core
        return out

    def step(self, feed, kill):
        u, v = self.u, self.v

        reaction = u * v * v

        lap_u = self._laplacian(u, self._lap_u)
        lap_v = self._laplacian(v, self._lap_v)

        u += DU * lap_u - reaction + feed * (1 - u)
        v += DV * lap_v + reaction - (feed + kill) * v


# Arguments ----------------------------------------------------------------


def _build_parser():
    parser = argparse.ArgumentParser(
        prog="termigrad",
        description="Run a Gray-Scott reaction-diffusion simulation in your terminal.",
    )

    parser.add_argument(
        "--preset",
        choices=sorted(PRESETS),
        default=DEFAULT_PRESET,
        help="pattern to start from (default: %(default)s)",
    )
    parser.add_argument(
        "--feed",
        type=float,
        default=None,
        metavar="F",
        help="override the preset feed rate",
    )
    parser.add_argument(
        "--kill",
        type=float,
        default=None,
        metavar="K",
        help="override the preset kill rate",
    )
    parser.add_argument(
        "--speed",
        type=float,
        default=1.0,
        metavar="X",
        help="speed multiplier, 0.5 for half speed, 0 for unlimited (default: %(default)s)",
    )
    parser.add_argument(
        "--no-colour",
        action="store_true",
        help="render in plain ASCII, without 24-bit colour",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="show the version and exit",
    )

    return parser


def main(argv=None):
    parser = _build_parser()
    args = parser.parse_args(argv)

    feed, kill = PRESETS[args.preset]
    if args.feed is not None:
        feed = args.feed
    if args.kill is not None:
        kill = args.kill

    dimension = shutil.get_terminal_size()
    shape = (dimension.lines, dimension.columns)

    if shape[0] < MIN_LINES or shape[1] < MIN_COLUMNS:
        sys.stderr.write(
            f"termigrad: terminal is {shape[1]}x{shape[0]}, "
            f"need at least {MIN_COLUMNS}x{MIN_LINES}. Try resizing.\n"
        )
        return 1

    field = Field(shape)

    tty = sys.stdout.isatty()
    out = sys.stdout.buffer
    colour = tty and not args.no_colour and not os.environ.get("NO_COLOR")

    interval = FRAME_INTERVAL / args.speed if args.speed > 0 else 0.0

    if tty:
        out.write(ENTER)
        out.flush()

    deadline = time.perf_counter()

    try:
        while True:
            for _ in range(SIMS_PER_FRAME):
                field.step(feed, kill)

            frame = render(field.v, colour=colour)
            out.write(FRAME + frame if tty else frame)
            out.flush()

            if tty:
                deadline += interval
                delay = deadline - time.perf_counter()
                if delay > 0.0:
                    time.sleep(delay)
                else:
                    deadline = time.perf_counter()

    except (KeyboardInterrupt, BrokenPipeError):
        pass

    finally:
        if tty:
            out.write(LEAVE)
            out.flush()

    return 0


# Entry point --------------------------------------------------------------


if __name__ == "__main__":
    sys.exit(main())
