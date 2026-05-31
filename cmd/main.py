from flask import Flask, render_template, request
from flask_socketio import SocketIO
import sys, os, threading, time
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from internal.logic import Ant

app = Flask(
    __name__,
    template_folder='../web',
    static_folder='../web/assets',
    static_url_path='/assets'
)
socketio = SocketIO(app, async_mode='threading')
sessions = {}
ZERO_MS_DELAY = 0.000001
FASTEST_FRAME_DELAY = 1 / 60
FASTEST_BATCH_SIZE = 100
FASTEST_CONTROL_DELAY = 0.001
DEFAULT_RULES = [
    {'color': '#ffffff', 'turn': 'left', 'next_color': 1},
    {'color': '#000000', 'turn': 'right', 'next_color': 0},
]

def normalize_rules(raw_rules):
    if not isinstance(raw_rules, list) or not raw_rules:
        return DEFAULT_RULES

    rules = []
    for index, raw_rule in enumerate(raw_rules):
        color = raw_rule.get('color', DEFAULT_RULES[index % len(DEFAULT_RULES)]['color'])
        turn = raw_rule.get('turn', 'right')
        next_color = raw_rule.get('next_color', (index + 1) % len(raw_rules))
        if turn not in Ant.turn_values:
            turn = 'right'
        try:
            next_color = int(next_color)
        except (TypeError, ValueError):
            next_color = (index + 1) % len(raw_rules)
        if next_color < 0 or next_color >= len(raw_rules):
            next_color = (index + 1) % len(raw_rules)
        rules.append({
            'color': color,
            'turn': turn,
            'next_color': next_color
        })
    return rules

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    sessions[request.sid] = {
        'simulation_running': False,
        'simulation_id': 0,
        'tickspeed': 500,
        'fastest_possible': False,
        'rules': DEFAULT_RULES,
        'speed_lock': threading.Lock(),
        'speed_changed': threading.Event(),
    }

@socketio.on('disconnect')
def handle_disconnect():
    session = sessions.pop(request.sid, None)
    if session:
        session['simulation_running'] = False
        session['speed_changed'].set()

def run_simulation(sid, current_simulation_id):
    session = sessions.get(sid)
    if not session:
        return
    speed_lock = session['speed_lock']
    speed_changed = session['speed_changed']
    try:
        tiles = {}
        langton = Ant()
        rules = session['rules']
        pending_updates = []
        last_emit = time.monotonic()
        while current_simulation_id == session['simulation_id']:
            if not session['simulation_running']:
                session['speed_changed'].wait()
                session['speed_changed'].clear()
                continue
            with speed_lock:
                current_tickspeed = session['tickspeed']
                current_fastest_possible = session['fastest_possible']
                speed_changed.clear()
            delay = current_tickspeed / 1000
            if current_tickspeed == 0 and not current_fastest_possible:
                delay = ZERO_MS_DELAY
            if delay > 0:
                if speed_changed.wait(delay):
                    continue
                prev_pos = tuple(langton.pos)
                langton.square_logic(tiles, rules)
                socketio.emit('tile_updates', {
                    'simulation_id': current_simulation_id,
                    'updates': [{
                        'x': prev_pos[0],
                        'y': prev_pos[1],
                        'color': tiles[prev_pos].color
                    }],
                    'ant_x': langton.pos[0],
                    'ant_y': langton.pos[1],
                    'ant_facing': langton.facing
                }, to=sid)
                continue
            prev_pos = tuple(langton.pos)
            langton.square_logic(tiles, rules)
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
                    'ant_y': langton.pos[1],
                    'ant_facing': langton.facing
                }, to=sid)
                pending_updates = []
                last_emit = now
                speed_changed.wait(FASTEST_CONTROL_DELAY)
    finally:
        if session and current_simulation_id == session['simulation_id']:
            session['simulation_running'] = False

@socketio.on('start')
def handle_start(data):
    session = sessions.get(request.sid)
    if not session:
        return
    with session['speed_lock']:
        session['tickspeed'] = float(data['tickspeed'])
        session['fastest_possible'] = data.get('fastest_possible', False)
        session['rules'] = normalize_rules(data.get('rules'))
        session['speed_changed'].set()
    session['simulation_id'] += 1
    current_simulation_id = session['simulation_id']
    session['simulation_running'] = True
    socketio.emit('simulation_started', {
        'simulation_id': current_simulation_id,
        'colors': [rule['color'] for rule in session['rules']]
    }, to=request.sid)
    thread = threading.Thread(target=run_simulation, args=(request.sid, current_simulation_id))
    thread.daemon = True
    thread.start()

@socketio.on('pause')
def handle_pause(data):
    session = sessions.get(request.sid)
    if not session:
        return
    session['simulation_running'] = not data['pause']
    session['speed_changed'].set()

@socketio.on('reset')
def handle_reset():
    session = sessions.get(request.sid)
    if not session:
        return
    session['simulation_running'] = False
    session['simulation_id'] += 1
    session['speed_changed'].set()

@socketio.on('tickspeed')
def handle_tickspeed(data):
    session = sessions.get(request.sid)
    if not session:
        return
    with session['speed_lock']:
        session['tickspeed'] = float(data['tickspeed'])
        session['speed_changed'].set()

@socketio.on('fastest_possible')
def handle_fastest_possible(data):
    session = sessions.get(request.sid)
    if not session:
        return
    with session['speed_lock']:
        session['fastest_possible'] = data['fastest_possible']
        session['speed_changed'].set()

@socketio.on('speed_settings')
def handle_speed_settings(data):
    session = sessions.get(request.sid)
    if not session:
        return
    with session['speed_lock']:
        session['tickspeed'] = float(data['tickspeed'])
        session['fastest_possible'] = data['fastest_possible']
        session['speed_changed'].set()

if __name__ == '__main__':
    print("Server running on http://localhost:5000")
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
