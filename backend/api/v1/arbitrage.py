from flask import Blueprint, jsonify, request
from backend.auth_utils import token_required
from backend.models.arbitrage import ArbitrageOpportunity, AlgorithmicTradeRecord
from backend.extensions import db

arbitrage_bp = Blueprint('arbitrage', __name__)

@arbitrage_bp.route('/opportunities', methods=['GET'])
@token_required
def list_active_arbitrage(current_user):
    """List open un-executed arbitrage opportunities > 12% margin."""
    min_margin = float(request.args.get('min_margin', 12.0))
    opps = ArbitrageOpportunity.query.filter(
        ArbitrageOpportunity.status == 'IDENTIFIED',
        ArbitrageOpportunity.gross_margin_pct >= min_margin
    ).order_by(ArbitrageOpportunity.gross_margin_pct.desc()).limit(50).all()
    
    return jsonify({
        'status': 'success',
        'count': len(opps),
        'data': [o.to_dict() for o in opps]
    })

@arbitrage_bp.route('/trades', methods=['GET'])
@token_required
def get_executed_bot_trades(current_user):
    """View highly profitable executed quantitative trades."""
    trades = AlgorithmicTradeRecord.query.order_by(AlgorithmicTradeRecord.executed_at.desc()).limit(100).all()
    
    data = []
    for t in trades:
        opp = ArbitrageOpportunity.query.get(t.opportunity_id)
        data.append({
            'trade_id': t.id,
            'opportunity': opp.to_dict(),
            'executed_volume_kg': t.execution_volume_kg,
            'realized_profit_usd': t.realized_profit_usd,
            'slippage_pct': t.slippage_pct,
            'timestamp': t.executed_at.isoformat()
        })
        
    return jsonify({
        'status': 'success',
        'count': len(data),
        'data': data
    })

@arbitrage_bp.route('/scan', methods=['POST'])
@token_required
def force_matrix_scan(current_user):
    """Manual overwrite endpoint to trigger global arbitrage sweep."""
    from backend.services.arbitrage_service import AlgorithmicArbitrageMatrix
    
    stats = AlgorithmicArbitrageMatrix.identify_arbitrage_vectors()
    
    return jsonify({
        'status': 'success',
        'message': 'Arbitrage matrix generated.',
        'metrics': stats
    }), 200
