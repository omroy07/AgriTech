from flask import Blueprint, request, jsonify
from backend.services.knowledge_service import KnowledgeService
from auth_utils import token_required
import logging

questions_bp = Blueprint('questions', __name__)

@questions_bp.route('/', methods=['GET'])
def get_questions():
    category = request.args.get('category')
    search = request.args.get('search')
    sort = request.args.get('sort', 'newest')
    
    questions = KnowledgeService.get_questions(category, search, sort)
    return jsonify({
        'status': 'success',
        'data': [q.to_dict() for q in questions]
    }), 200

@questions_bp.route('/<int:question_id>', methods=['GET'])
def get_question_detail(question_id):
    from backend.models.knowledge import Question
    question = Question.query.get_or_404(question_id)
    
    # Increment view count
    question.view_count += 1
    from backend.extensions import db
    db.session.commit()
    
    data = question.to_dict()
    data['answers'] = [a.to_dict() for a in question.answers.order_by(Answer.upvote_count.desc()).all()]
    
    return jsonify({
        'status': 'success',
        'data': data
    }), 200

@questions_bp.route('/', methods=['POST'])
@token_required
def create_question(current_user):
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data:
        return jsonify({'status': 'error', 'message': 'Missing title or content'}), 400
        
    question, error = KnowledgeService.create_question(
        user_id=current_user.id,
        title=data['title'],
        content=data['content'],
        category=data.get('category', 'General')
    )
    
    if error:
        return jsonify({'status': 'error', 'message': error}), 500
        
    return jsonify({
        'status': 'success',
        'data': question.to_dict()
    }), 201

@questions_bp.route('/<int:question_id>/vote', methods=['POST'])
@token_required
def vote_question(current_user, question_id):
    success, error = KnowledgeService.vote_item(current_user.id, 'question', question_id)
    if not success:
        return jsonify({'status': 'error', 'message': error}), 400
        
    return jsonify({'status': 'success', 'message': 'Vote recorded'}), 200
