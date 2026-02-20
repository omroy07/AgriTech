from flask import Blueprint, request, jsonify
from backend.services.knowledge_service import KnowledgeService
from auth_utils import token_required

answers_bp = Blueprint('answers', __name__)

@answers_bp.route('/', methods=['POST'])
@token_required
def add_answer(current_user):
    data = request.get_json()
    if not data or 'question_id' not in data or 'content' not in data:
        return jsonify({'status': 'error', 'message': 'Missing data'}), 400
        
    answer, error = KnowledgeService.add_answer(
        question_id=data['question_id'],
        user_id=current_user.id,
        content=data['content']
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    # Trigger socket notification here in real app
    
    return jsonify({
        'status': 'success',
        'data': answer.to_dict()
    }), 201

@answers_bp.route('/<int:answer_id>/vote', methods=['POST'])
@token_required
def vote_answer(current_user, answer_id):
    success, error = KnowledgeService.vote_item(current_user.id, 'answer', answer_id)
    if not success:
        return jsonify({'status': 'error', 'message': error}), 400
        
    return jsonify({'status': 'success', 'message': 'Vote recorded'}), 200

@answers_bp.route('/<int:answer_id>/accept', methods=['POST'])
@token_required
def accept_answer(current_user, answer_id):
    success, error = KnowledgeService.accept_answer(current_user.id, answer_id)
    if not success:
        return jsonify({'status': 'error', 'message': error}), 400
        
    return jsonify({'status': 'success', 'message': 'Answer accepted'}), 200
