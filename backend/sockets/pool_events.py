"""
Real-time SocketIO events for yield pool voting and updates.
"""

from flask_socketio import emit, join_room, leave_room
from backend.services.pool_service import PoolService
from backend.models import YieldPool, PoolVote
import logging

logger = logging.getLogger(__name__)


def register_pool_events(socketio):
    """Register all pool-related SocketIO event handlers."""
    
    @socketio.on('join_pool_room')
    def handle_join_pool(data):
        """Join a pool's SocketIO room for real-time updates."""
        pool_id = data.get('pool_id')
        user_id = data.get('user_id')
        
        if not pool_id:
            emit('error', {'message': 'pool_id is required'})
            return
        
        room = f'pool_{pool_id}'
        join_room(room)
        
        logger.info(f"User {user_id} joined pool room: {room}")
        
        # Send current pool status
        stats = PoolService.get_pool_statistics(pool_id)
        if stats:
            emit('pool_status', stats)
        
        emit('joined_room', {'pool_id': pool_id, 'room': room})
    
    @socketio.on('leave_pool_room')
    def handle_leave_pool(data):
        """Leave a pool's SocketIO room."""
        pool_id = data.get('pool_id')
        user_id = data.get('user_id')
        
        if not pool_id:
            emit('error', {'message': 'pool_id is required'})
            return
        
        room = f'pool_{pool_id}'
        leave_room(room)
        
        logger.info(f"User {user_id} left pool room: {room}")
        emit('left_room', {'pool_id': pool_id})
    
    @socketio.on('cast_vote')
    def handle_cast_vote(data):
        """Cast a vote on a pool offer in real-time."""
        pool_id = data.get('pool_id')
        user_id = data.get('user_id')
        vote = data.get('vote')
        comment = data.get('comment')
        
        if not pool_id or not user_id or not vote:
            emit('error', {'message': 'pool_id, user_id, and vote are required'})
            return
        
        if vote not in ['ACCEPT', 'REJECT']:
            emit('error', {'message': 'vote must be ACCEPT or REJECT'})
            return
        
        # Record vote
        pool_vote, error = PoolService.record_vote(pool_id, user_id, vote, comment)
        
        if error:
            emit('vote_error', {'message': error})
            return
        
        # Broadcast vote to all pool members
        room = f'pool_{pool_id}'
        voting_status = PoolService.get_voting_status(pool_id)
        
        socketio.emit('vote_cast', {
            'voter_id': user_id,
            'vote': vote,
            'voting_status': voting_status,
            'timestamp': pool_vote.voted_at.isoformat()
        }, room=room)
        
        logger.info(f"Vote broadcast: User {user_id} voted {vote} on pool {pool_id}")
        
        # Check if voting is complete
        if voting_status and voting_status.get('voting_complete'):
            consensus = voting_status.get('consensus_reached')
            socketio.emit('voting_complete', {
                'pool_id': pool_id,
                'consensus_reached': consensus,
                'result': 'ACCEPTED' if consensus else 'REJECTED',
                'voting_status': voting_status
            }, room=room)
            
            logger.info(f"Voting complete for pool {pool_id}: {'ACCEPTED' if consensus else 'REJECTED'}")
    
    @socketio.on('update_offer')
    def handle_update_offer(data):
        """Broadcast a new buyer offer to pool members."""
        pool_id = data.get('pool_id')
        buyer_name = data.get('buyer_name')
        offer_price = data.get('offer_price')
        
        if not pool_id or not buyer_name or not offer_price:
            emit('error', {'message': 'pool_id, buyer_name, and offer_price are required'})
            return
        
        # Set offer in database
        success, error = PoolService.set_buyer_offer(pool_id, buyer_name, offer_price)
        
        if not success:
            emit('offer_error', {'message': error})
            return
        
        # Broadcast to all pool members
        room = f'pool_{pool_id}'
        socketio.emit('new_offer', {
            'pool_id': pool_id,
            'buyer_name': buyer_name,
            'offer_price': offer_price,
            'message': f'New offer from {buyer_name}: ₹{offer_price}/ton'
        }, room=room)
        
        logger.info(f"New offer broadcast for pool {pool_id}: {buyer_name} at {offer_price}/ton")
    
    @socketio.on('pool_state_change')
    def handle_state_change(data):
        """Broadcast pool state changes to members."""
        pool_id = data.get('pool_id')
        new_state = data.get('state')
        user_id = data.get('user_id')
        
        if not pool_id or not new_state:
            emit('error', {'message': 'pool_id and state are required'})
            return
        
        # Transition state
        success, error = PoolService.transition_state(pool_id, new_state, user_id)
        
        if not success:
            emit('state_error', {'message': error})
            return
        
        # Broadcast to all pool members
        room = f'pool_{pool_id}'
        socketio.emit('state_changed', {
            'pool_id': pool_id,
            'new_state': new_state,
            'message': f'Pool transitioned to {new_state}'
        }, room=room)
        
        logger.info(f"State change broadcast for pool {pool_id}: {new_state}")
    
    @socketio.on('contribution_added')
    def handle_contribution_notification(data):
        """Broadcast when a new contribution is added."""
        pool_id = data.get('pool_id')
        user_id = data.get('user_id')
        quantity_tons = data.get('quantity_tons')
        
        if not pool_id:
            return
        
        # Get updated pool stats
        stats = PoolService.get_pool_statistics(pool_id)
        
        if not stats:
            return
        
        # Broadcast to pool room
        room = f'pool_{pool_id}'
        socketio.emit('contribution_update', {
            'pool_id': pool_id,
            'contributor_id': user_id,
            'quantity_tons': quantity_tons,
            'current_quantity': stats['total_quantity'],
            'fill_percentage': stats['fill_percentage'],
            'message': f'New contribution: {quantity_tons} tons added'
        }, room=room)
        
        logger.info(f"Contribution update broadcast for pool {pool_id}")
    
    @socketio.on('request_pool_status')
    def handle_status_request(data):
        """Request current pool status."""
        pool_id = data.get('pool_id')
        
        if not pool_id:
            emit('error', {'message': 'pool_id is required'})
            return
        
        stats = PoolService.get_pool_statistics(pool_id)
        
        if not stats:
            emit('error', {'message': 'Pool not found'})
            return
        
        emit('pool_status', stats)
    
    logger.info("Pool SocketIO events registered")


# Helper functions for triggering events from other parts of the application

def broadcast_pool_update(socketio, pool_id, event_type, data):
    """
    Helper function to broadcast pool updates from anywhere in the application.
    
    Args:
        socketio: SocketIO instance
        pool_id (int): Pool database ID
        event_type (str): Type of event to broadcast
        data (dict): Event data
    """
    room = f'pool_{pool_id}'
    socketio.emit(event_type, data, room=room)
    logger.info(f"Broadcast {event_type} to pool {pool_id}")


def notify_pool_members(socketio, pool_id, message, notification_type='info'):
    """
    Send a notification to all pool members.
    
    Args:
        socketio: SocketIO instance
        pool_id (int): Pool database ID
        message (str): Notification message
        notification_type (str): Type of notification (info, warning, success, error)
    """
    room = f'pool_{pool_id}'
    socketio.emit('pool_notification', {
        'pool_id': pool_id,
        'message': message,
        'type': notification_type
    }, room=room)
    logger.info(f"Notification sent to pool {pool_id}: {message}")
