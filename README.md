# termigrad

A terminal-based ascii visualiser for the Gray Scott Reaction-Diffusion model.

## Installation

```bash
pip install termigrad
termigrad -h
```

## Features

- Simplistic, readable, highly extensible codebase
- Minimalist, colour ascii graphics
- Highly customisable parameters for the Gray Scott model

## Usage

Run with no arguments to start the `stripes` preset. Press `Ctrl-C` to stop.

```bash
termigrad
```

### Options

| Flag            | Description                                                                                                              |
| --------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `--preset NAME` | Preset parameters to start with! Accepts any of `coral`, `mooncake`, `spots`, `stripes`, `worms`. Defaults to `stripes`. |
| `--feed F`      | Override the preset feed rate with custom input.                                                                         |
| `--kill K`      | Override the preset kill rate with custom kill.                                                                          |
| `--speed X`     | Speed multiplier, intuitively `0.5` for half speed, `2` for double, `0` for unlimited. Defaults to `1.0`.                |
| `--no-colour`   | Render in plain ASCII, without colour :<.                                                                                |
| `--version`     | Print the version and exit.                                                                                              |

### Presets

Each preset is a feed/kill pair for the Gray-Scott model:

| Preset     | Feed (F) | Kill (k) | Pattern                  |
| ---------- | -------- | -------- | ------------------------ |
| `spots`    | 0.0367   | 0.0649   | Spots, mitosis           |
| `coral`    | 0.0545   | 0.0620   | Coral, branching         |
| `worms`    | 0.0300   | 0.0620   | Worms, moving structures |
| `stripes`  | 0.0220   | 0.0510   | Stripes (default)        |
| `mooncake` | 0.0400   | 0.0600   | Moon cake                |

The diffusion rates are fixed at `dU = 0.160` and `dV = 0.080`.

For anything outside the presets, pass your own feed and kill rates:

```bash
termigrad --preset worms --feed 0.026
```

### Colour

Output uses 24-bit colour where the terminal supports it, and falls back to
plain ASCII when stdout is not a TTY. Colour is also disabled automatically when
the `NO_COLOR` environment variable is set, or with `--no-colour`.

## Requirements

Python 3.9 or newer, and [numpy](https://numpy.org/). Needs a terminal of at
least 60x24 (I mean it should work no matter, but to see anything interesting requires a decently large terminal).
