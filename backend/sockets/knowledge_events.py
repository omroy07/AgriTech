from flask_socketio import emit, join_room
from backend.extensions import socketio
import logging

logger = logging.getLogger(__name__)

@socketio.on('join_knowledge_hub', namespace='/knowledge')
def on_join(data):
    """Users join a general knowledge hub for live updates"""
    join_room('knowledge_feed')
    logger.info("A user joined the knowledge hub feed.")

@socketio.on('subscribe_question', namespace='/knowledge')
def on_subscribe_question(data):
    """Subscribe to updates for a specific question"""
    question_id = data.get('question_id')
    if question_id:
        join_room(f"question_{question_id}")
        logger.info(f"User subscribed to question {question_id}")

def broadcast_new_answer(question_id, answer_data):
    """Notify subscribers when a new answer is posted"""
    socketio.emit(
        'new_answer_received',
        answer_data,
        room=f"question_{question_id}",
        namespace='/knowledge'
    )
    
    # Also notify the general feed
    socketio.emit(
        'feed_update',
        {'type': 'new_answer', 'question_id': question_id},
        room='knowledge_feed',
        namespace='/knowledge'
    )
