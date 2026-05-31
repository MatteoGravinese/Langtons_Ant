# Langton's Ant Simulator

An interactive, browser-based simulator for **Langton's Ant** — a two-dimensional Turing machine that produces surprisingly complex emergent behaviour from a handful of simple rules.

Built with a Python/Flask + Socket.IO backend that runs the simulation server-side and streams state updates to the browser in real time.

![Langton's Ant](web/assets/ant.png)

---

## What is Langton's Ant?

Langton's Ant is a cellular automaton defined on an infinite grid. An ant starts at the origin and follows these rules on each step:

1. Look at the colour of the current square.
2. Apply the rule for that colour: turn left, turn right, or rotate 180°, then change the square to the next colour.
3. Move one step forward in the new facing direction.

With the classic two-colour ruleset the ant wanders chaotically for ~10,000 steps, then spontaneously constructs an infinitely repeating "highway" pattern — a striking example of emergent order from simple rules.

This simulator extends the classic ruleset to support **any number of colours**, fully configurable turn directions and colour transitions.

---

## Features

- **Infinite grid** — pan and zoom freely; the grid has no bounds
- **Custom colour rules** — add as many colours as you like, each with its own turn direction and colour transition (including leaving a square unchanged)
- **Real-time streaming** — the simulation runs on the server and pushes updates to the browser via Socket.IO
- **Adjustable step delay** — drag the slider from *Instant* (maximum speed, batched updates) to 1000 ms per step
- **Pause / resume** at any time
- **Centre on Ant** — instantly re-centre the camera on the ant's current position

---

## Project Structure

```
Langtons_Ant/
├── cmd/
│   └── main.py          # Flask + Socket.IO server, simulation runner
├── internal/
│   └── logic.py         # Ant and Tile classes (core simulation logic)
├── web/
│   ├── index.html       # Browser UI (canvas renderer + Socket.IO client)
│   └── assets/
│       └── ant.png      # Ant sprite
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### Install dependencies

```bash
pip install flask flask-socketio
```

### Run the server

```bash
python cmd/main.py
```

Then open **http://localhost:5000** in your browser.

> **Note:** `python -m http.server` will not work — the app requires the Flask server for Socket.IO support and asset routing.

---

## Usage

1. **Configure colour rules** in the sidebar. Each rule defines:
   - The square colour it applies to
   - The direction the ant turns (`Left 90`, `Right 90`, `Rotate 180`)
   - The colour the square changes to (select the same colour to leave it unchanged)
2. Click **Start Simulation** to begin.
3. **Pan** by clicking and dragging the canvas.
4. **Zoom** with the scroll wheel or a pinch gesture.
5. Use the **Step Delay** slider to control speed. Drag it fully left for maximum speed.
   - At maximum speed, tick the **Run at maximum speed** checkbox to enable batched updates for even higher throughput.
6. Click **Pause Simulation** / **Resume Simulation** to pause and continue.
7. Click **Centre on Ant** to snap the camera back to the ant.
8. Click **Reset Grid** to clear the board and start over with new rules.

---

## How It Works

The simulation runs entirely on the server in a dedicated thread per client session. On each tick the server:

1. Reads the current tile colour under the ant.
2. Looks up the matching rule and updates the ant's direction and the tile's colour.
3. Moves the ant forward one step.
4. Emits a `tile_updates` Socket.IO event to the client with the changed tile and new ant position.

At maximum speed, updates are batched (up to 100 steps) and emitted at ~60 fps to avoid overwhelming the client.

Speed changes take effect immediately via a `speed_changed` threading event — no restart required.

---

## License

MIT
