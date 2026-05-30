from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import sys, os, threading
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from internal.logic import Tile, Ant

app = Flask(__name__, template_folder='../web')
socketio = SocketIO(app)
simulation_running = False
tickspeed = 500

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    global simulation_running
    simulation_running = False

def run_simulation(x_size, y_size, wrap):
    global simulation_running, tickspeed
    try:
        tiles = {(x, y): Tile(x, y) for x in range(x_size) for y in range(y_size)}
        langton = Ant(x_size // 2, y_size // 2)
        safe = True
        while safe:
            prev_pos = tuple(langton.pos)
            safe = langton.square_logic(tiles, x_size, y_size)
            socketio.emit('tile_update', {
                'x': prev_pos[0],
                'y': prev_pos[1],
                'color': tiles[prev_pos].color
            })
            socketio.sleep(max(tickspeed / 1000, 0.000001))
    finally:
        simulation_running = False

@socketio.on('start')
def handle_start(data):
    global simulation_running, tickspeed
    tickspeed = float(data['tickspeed'])
    if simulation_running:
        return
    simulation_running = True
    x_size = int(data['x_size'])
    y_size = int(data['y_size'])
    wrap = data['wrap']
    thread = threading.Thread(target=run_simulation, args=(x_size, y_size, wrap))
    thread.daemon = True
    thread.start()

@socketio.on('tickspeed')
def handle_tickspeed(data):
    global tickspeed
    tickspeed = float(data['tickspeed'])

if __name__ == '__main__':
    print("Server running on http://localhost:5000")
    socketio.run(app, debug=True)