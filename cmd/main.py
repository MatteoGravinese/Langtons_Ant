from flask import Flask, render_template
from flask_socketio import SocketIO
import sys, os, threading, time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from internal.logic import Ant

app = Flask(__name__, template_folder='../web')
socketio = SocketIO(app, async_mode='threading')
simulation_running = False
simulation_id = 0
tickspeed = 500
fastest_possible = False
speed_lock = threading.Lock()
speed_changed = threading.Event()
ZERO_MS_DELAY = 0.000001
FASTEST_FRAME_DELAY = 1 / 60
FASTEST_BATCH_SIZE = 100
FASTEST_CONTROL_DELAY = 0.001

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global simulation_running, simulation_id
    simulation_running = False
    simulation_id += 1

def run_simulation(current_simulation_id):
    global simulation_running
    try:
        tiles = {}
        langton = Ant()
        pending_updates = []
        last_emit = time.monotonic()
        while simulation_running and current_simulation_id == simulation_id:
            with speed_lock:
                current_tickspeed = tickspeed
                current_fastest_possible = fastest_possible
                speed_changed.clear()

            delay = current_tickspeed / 1000
            if current_tickspeed == 0 and not current_fastest_possible:
                delay = ZERO_MS_DELAY

            if delay > 0:
                if speed_changed.wait(delay):
                    continue

                prev_pos = tuple(langton.pos)
                langton.square_logic(tiles)
                socketio.emit('tile_updates', {
                    'simulation_id': current_simulation_id,
                    'updates': [{
                        'x': prev_pos[0],
                        'y': prev_pos[1],
                        'color': tiles[prev_pos].color
                    }],
                    'ant_x': langton.pos[0],
                    'ant_y': langton.pos[1]
                })
                continue

            prev_pos = tuple(langton.pos)
            langton.square_logic(tiles)
            pending_updates.append({
                'x': prev_pos[0],
                'y': prev_pos[1],
                'color': tiles[prev_pos].color
            })

            now = time.monotonic()
            if speed_changed.is_set() or len(pending_updates) >= FASTEST_BATCH_SIZE or now - last_emit >= FASTEST_FRAME_DELAY:
                socketio.emit('tile_updates', {
                    'simulation_id': current_simulation_id,
                    'updates': pending_updates,
                    'ant_x': langton.pos[0],
                    'ant_y': langton.pos[1]
                })
                pending_updates = []
                last_emit = now
                speed_changed.wait(FASTEST_CONTROL_DELAY)
    finally:
        if current_simulation_id == simulation_id:
            simulation_running = False

@socketio.on('start')
def handle_start(data):
    global simulation_running, simulation_id, tickspeed, fastest_possible
    with speed_lock:
        tickspeed = float(data['tickspeed'])
        fastest_possible = data.get('fastest_possible', False)
        speed_changed.set()
    simulation_id += 1
    current_simulation_id = simulation_id
    simulation_running = True
    socketio.emit('simulation_started', {
        'simulation_id': current_simulation_id
    })
    thread = threading.Thread(target=run_simulation, args=(current_simulation_id,))
    thread.daemon = True
    thread.start()

@socketio.on('tickspeed')
def handle_tickspeed(data):
    global tickspeed
    with speed_lock:
        tickspeed = float(data['tickspeed'])
        speed_changed.set()

@socketio.on('fastest_possible')
def handle_fastest_possible(data):
    global fastest_possible
    with speed_lock:
        fastest_possible = data['fastest_possible']
        speed_changed.set()

@socketio.on('speed_settings')
def handle_speed_settings(data):
    global tickspeed, fastest_possible
    with speed_lock:
        tickspeed = float(data['tickspeed'])
        fastest_possible = data['fastest_possible']
        speed_changed.set()

if __name__ == '__main__':
    print("Server running on http://localhost:5000")
    socketio.run(app, debug=True)
