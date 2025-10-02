from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, send, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'
socketio = SocketIO(app, cors_allowed_origins="*")

# room_name: set(usernames)
communities = {}

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/communities", methods=['GET'])
def get_communities():
    return jsonify(list(communities.keys()))

@app.route("/add_community", methods=['POST'])
def add_community():
    room = request.json.get('room')
    if room and room not in communities:
        communities[room] = set()
        return jsonify({"success": True, "communities": list(communities.keys())})
    return jsonify({"success": False, "communities": list(communities.keys())})

@app.route("/delete_community", methods=['POST'])
def delete_community():
    room = request.json.get('room')
    if room in communities and len(communities[room]) == 0:
        del communities[room]
        return jsonify({"success": True, "communities": list(communities.keys())})
    return jsonify({"success": False, "error": "Room not empty or doesn't exist", "communities": list(communities.keys())})

@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    if room not in communities:
        communities[room] = set()
    join_room(room)
    communities[room].add(username)
    send({'msg': f'{username} joined {room}'}, room=room)
    emit('user_list', list(communities[room]), room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['room']
    leave_room(room)
    if room in communities and username in communities[room]:
        communities[room].remove(username)
        send({'msg': f'{username} left {room}'}, room=room)
        emit('user_list', list(communities[room]), room=room)

@socketio.on('message')
def handle_message(data):
    room = data['room']
    username = data['username']
    msg = data['msg']
    from datetime import datetime
    timestamp = datetime.now().strftime('%H:%M')
    send({'msg': f'[{timestamp}] {username}: {msg}'}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
