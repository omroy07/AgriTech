"""
WebSocket Client Usage Example
==============================

This file demonstrates how to connect to the AgriTech WebSocket server
and receive real-time task updates.

JavaScript Example:
-------------------

// Connect to WebSocket server
const socket = io('http://localhost:5000');

// Connection established
socket.on('connected', (data) => {
    console.log('Connected:', data.message);
});

// Submit a task and join the room
async function submitCropPrediction(data) {
    // Submit the async task
    const response = await fetch('/api/crop/predict-async', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    const result = await response.json();
    
    // Join the task room to receive updates
    socket.emit('join_task', { task_id: result.task_id });
    
    return result.task_id;
}

// Listen for task updates
socket.on('task_started', (data) => {
    console.log('Task started:', data.task_id);
    showLoading();
});

socket.on('task_completed', (data) => {
    console.log('Task completed:', data);
    displayResult(data.result);
    
    // Leave the room when done
    socket.emit('leave_task', { task_id: data.task_id });
});

socket.on('task_failed', (data) => {
    console.error('Task failed:', data.error);
    showError(data.error);
    
    // Leave the room
    socket.emit('leave_task', { task_id: data.task_id });
});

// Example usage
const taskId = await submitCropPrediction({
    N: 50, P: 40, K: 30,
    temperature: 25.5,
    humidity: 80,
    ph: 6.5,
    rainfall: 200
});

console.log('Submitted task:', taskId);
// Now just wait for the socket events!

Python Example:
---------------

import socketio

sio = socketio.Client()

@sio.on('connected')
def on_connect(data):
    print('Connected:', data['message'])

@sio.on('task_completed')
def on_task_completed(data):
    print('Task completed:', data['result'])

# Connect
sio.connect('http://localhost:5000')

# Join task room
sio.emit('join_task', {'task_id': 'abc123'})

# Wait for events
sio.wait()
"""
