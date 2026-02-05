from flask import Blueprint, request, jsonify
from backend.services.forum_service import forum_service
from backend.services.ai_moderator import ai_moderator
from backend.models import ForumCategory
from auth_utils import token_required
from backend.utils.logger import logger

forum_bp = Blueprint('forum', __name__)


@forum_bp.route('/forum/categories', methods=['GET'])
def get_categories():
    """Get all forum categories"""
    try:
        categories = ForumCategory.query.all()
        return jsonify({
            'status': 'success',
            'data': [c.to_dict() for c in categories]
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@forum_bp.route('/forum/categories', methods=['POST'])
@token_required
def create_category():
    """Create a new forum category (Admin only)"""
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        icon = data.get('icon')
        
        if not name:
            return jsonify({'status': 'error', 'message': 'Category name is required'}), 400
        
        category, error = forum_service.create_category(name, description, icon)
        if error:
            return jsonify({'status': 'error', 'message': error}), 500
        
        return jsonify({
            'status': 'success',
            'data': category.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@forum_bp.route('/forum/threads', methods=['GET'])
def get_threads():
    """
    Search and filter threads
    Query params: q (search), category_id, tags (comma-separated), sort_by, limit
    """
    try:
        query = request.args.get('q', '')
        category_id = request.args.get('category_id', type=int)
        tags_str = request.args.get('tags', '')
        sort_by = request.args.get('sort_by', 'relevance')
        limit = request.args.get('limit', 20, type=int)
        
        tags = [t.strip() for t in tags_str.split(',')] if tags_str else None
        
        threads, error = forum_service.search_threads(
            query=query,
            category_id=category_id,
            tags=tags,
            sort_by=sort_by,
            limit=min(limit, 100)  # Cap at 100
        )
        
        if error:
            return jsonify({'status': 'error', 'message': error}), 500
        
        return jsonify({
            'status': 'success',
            'data': threads,
            'count': len(threads)
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@forum_bp.route('/forum/threads/<int:thread_id>', methods=['GET'])
def get_thread(thread_id):
    """Get thread details with comments"""
    try:
        thread, error = forum_service.get_thread_details(thread_id, increment_view=True)
        if error:
            return jsonify({'status': 'error', 'message': error}), 404
        
        return jsonify({
            'status': 'success',
            'data': thread
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@forum_bp.route('/forum/threads', methods=['POST'])
@token_required
def create_thread():
    """Create a new thread"""
    try:
        user = request.user
        data = request.get_json()
        
        category_id = data.get('category_id')
        title = data.get('title')
        content = data.get('content')
        tags = data.get('tags', [])
        
        if not all([category_id, title, content]):
            return jsonify({
                'status': 'error',
                'message': 'category_id, title, and content are required'
            }), 400
        
        thread, error = forum_service.create_thread(
            user_id=user['id'],
            category_id=category_id,
            title=title,
            content=content,
            tags=tags
        )
        
        if error:
            return jsonify({'status': 'error', 'message': error}), 500
        
        return jsonify({
            'status': 'success',
            'data': thread.to_dict(),
            'message': 'Thread created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@forum_bp.route('/forum/threads/<int:thread_id>/comments', methods=['POST'])
@token_required
def create_comment(thread_id):
    """Add a comment or reply to a thread"""
    try:
        user = request.user
        data = request.get_json()
        
        content = data.get('content')
        parent_id = data.get('parent_id')  # For nested replies
        
        if not content:
            return jsonify({'status': 'error', 'message': 'Content is required'}), 400
        
        comment, error = forum_service.create_comment(
            user_id=user['id'],
            thread_id=thread_id,
            content=content,
            parent_id=parent_id
        )
        
        if error:
            return jsonify({'status': 'error', 'message': error}), 500
        
        return jsonify({
            'status': 'success',
            'data': comment.to_dict(),
            'message': 'Comment posted successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@forum_bp.route('/forum/threads/<int:thread_id>/upvote', methods=['POST'])
@token_required
def upvote_thread(thread_id):
    """Toggle upvote on a thread"""
    try:
        user = request.user
        result, error = forum_service.toggle_upvote(user_id=user['id'], thread_id=thread_id)
        
        if error:
            return jsonify({'status': 'error', 'message': error}), 500
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@forum_bp.route('/forum/comments/<int:comment_id>/upvote', methods=['POST'])
@token_required
def upvote_comment(comment_id):
    """Toggle upvote on a comment"""
    try:
        user = request.user
        result, error = forum_service.toggle_upvote(user_id=user['id'], comment_id=comment_id)
        
        if error:
            return jsonify({'status': 'error', 'message': error}), 500
        
        return jsonify({
            'status': 'success',
            'data': result
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@forum_bp.route('/forum/trending', methods=['GET'])
def get_trending():
    """Get trending threads"""
    try:
        limit = request.args.get('limit', 10, type=int)
        threads, error = forum_service.get_trending_threads(limit=min(limit, 50))
        
        if error:
            return jsonify({'status': 'error', 'message': error}), 500
        
        return jsonify({
            'status': 'success',
            'data': threads
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@forum_bp.route('/forum/unanswered', methods=['GET'])
def get_unanswered():
    """Get unanswered threads"""
    try:
        limit = request.args.get('limit', 10, type=int)
        threads, error = forum_service.get_unanswered_threads(limit=min(limit, 50))
        
        if error:
            return jsonify({'status': 'error', 'message': error}), 500
        
        return jsonify({
            'status': 'success',
            'data': threads
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@forum_bp.route('/forum/search-ai', methods=['GET'])
def ai_search():
    """AI-powered knowledge base search"""
    try:
        query = request.args.get('q', '')
        limit = request.args.get('limit', 5, type=int)
        
        if not query:
            return jsonify({'status': 'error', 'message': 'Query parameter q is required'}), 400
        
        results = ai_moderator.search_knowledge_base(query, limit=min(limit, 10))
        
        return jsonify({
            'status': 'success',
            'data': results,
            'query': query
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@forum_bp.route('/forum/flag', methods=['POST'])
@token_required
def flag_content():
    """Flag inappropriate content"""
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        comment_id = data.get('comment_id')
        reason = data.get('reason', 'User reported')
        
        result, error = forum_service.flag_content(
            thread_id=thread_id,
            comment_id=comment_id,
            reason=reason
        )
        
        if error:
            return jsonify({'status': 'error', 'message': error}), 500
        
        return jsonify({
            'status': 'success',
            'message': 'Content flagged for review'
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@forum_bp.route('/forum/reputation/<int:user_id>', methods=['GET'])
def get_reputation(user_id):
    """Get user reputation and stats"""
    try:
        reputation, error = forum_service.get_user_reputation(user_id)
        if error:
            return jsonify({'status': 'error', 'message': error}), 500
        
        stats, stat_error = forum_service.get_user_stats(user_id)
        if stat_error:
            stats = {}
        
        return jsonify({
            'status': 'success',
            'data': {
                'reputation': reputation,
                'stats': stats
            }
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
