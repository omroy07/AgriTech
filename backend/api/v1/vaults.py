"""
Vaults API: Endpoints for vault management and ledger auditing.

This module provides:
- Vault CRUD operations
- Deposit/withdrawal endpoints
- Transfer between vaults
- Ledger history and auditing
- FX revaluation endpoints
"""

from flask import Blueprint, jsonify, request
from decimal import Decimal
from datetime import datetime

from backend.auth_utils import token_required
from backend.services.vault_service import VaultService
from backend.services.ledger_service import LedgerService
from backend.services.fx_service import FXService
from backend.models.ledger import Vault, LedgerTransaction

vaults_bp = Blueprint('vaults', __name__)


@vaults_bp.route('/', methods=['POST'])
@token_required
def create_vault(current_user):
    """
    Create a new multi-currency vault.
    
    Request body:
    {
        "name": "Main Trading Vault",
        "base_currency": "USD",
        "allow_multi_currency": true,
        "auto_fx_revaluation": true
    }
    """
    data = request.get_json()
    
    if not data.get('name'):
        return jsonify({'error': 'Vault name is required'}), 400
    
    try:
        vault = VaultService.create_vault(
            name=data['name'],
            owner_type='user',
            owner_id=current_user.id,
            base_currency=data.get('base_currency', 'USD'),
            allow_multi_currency=data.get('allow_multi_currency', True),
            auto_fx_revaluation=data.get('auto_fx_revaluation', True)
        )
        
        return jsonify({
            'status': 'success',
            'vault': vault.to_dict()
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@vaults_bp.route('/', methods=['GET'])
@token_required
def list_vaults(current_user):
    """List all vaults owned by current user."""
    vaults = Vault.query.filter_by(
        owner_type='user',
        owner_id=current_user.id,
        is_active=True
    ).all()
    
    return jsonify({
        'status': 'success',
        'vaults': [v.to_dict() for v in vaults],
        'count': len(vaults)
    })


@vaults_bp.route('/<vault_id>', methods=['GET'])
@token_required
def get_vault(current_user, vault_id):
    """Get vault details with current balances."""
    vault = VaultService.get_vault(vault_id)
    
    if not vault:
        return jsonify({'error': 'Vault not found'}), 404
    
    if vault.owner_type == 'user' and vault.owner_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    balances = VaultService.get_vault_balances(vault)
    
    return jsonify({
        'status': 'success',
        'vault': vault.to_dict(include_positions=True),
        'balances': balances
    })


@vaults_bp.route('/<vault_id>/deposit', methods=['POST'])
@token_required
def deposit(current_user, vault_id):
    """
    Deposit funds into vault.
    
    Request body:
    {
        "amount": 1000.00,
        "currency": "EUR",
        "fx_rate": 1.08,  // optional, will fetch current if not provided
        "description": "Wire transfer",
        "reference": "TXN-12345"
    }
    """
    vault = VaultService.get_vault(vault_id)
    
    if not vault:
        return jsonify({'error': 'Vault not found'}), 404
    
    if vault.owner_type == 'user' and vault.owner_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if not data.get('amount') or data['amount'] <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    currency = data.get('currency', vault.base_currency)
    
    try:
        result = VaultService.deposit(
            vault=vault,
            amount=Decimal(str(data['amount'])),
            currency=currency,
            fx_rate=Decimal(str(data['fx_rate'])) if data.get('fx_rate') else None,
            source_description=data.get('description'),
            reference=data.get('reference'),
            created_by=current_user.id
        )
        
        return jsonify({
            'status': 'success',
            'deposit': result
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@vaults_bp.route('/<vault_id>/withdraw', methods=['POST'])
@token_required
def withdraw(current_user, vault_id):
    """
    Withdraw funds from vault.
    
    Request body:
    {
        "amount": 500.00,
        "currency": "EUR",
        "fx_rate": 1.09,  // optional
        "description": "Wire transfer out",
        "reference": "WD-12345"
    }
    """
    vault = VaultService.get_vault(vault_id)
    
    if not vault:
        return jsonify({'error': 'Vault not found'}), 404
    
    if vault.owner_type == 'user' and vault.owner_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json()
    
    if not data.get('amount') or data['amount'] <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    currency = data.get('currency', vault.base_currency)
    
    try:
        result = VaultService.withdraw(
            vault=vault,
            amount=Decimal(str(data['amount'])),
            currency=currency,
            fx_rate=Decimal(str(data['fx_rate'])) if data.get('fx_rate') else None,
            destination_description=data.get('description'),
            reference=data.get('reference'),
            created_by=current_user.id
        )
        
        return jsonify({
            'status': 'success',
            'withdrawal': result
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@vaults_bp.route('/transfer', methods=['POST'])
@token_required
def transfer(current_user):
    """
    Transfer funds between vaults.
    
    Request body:
    {
        "source_vault_id": "uuid-1",
        "dest_vault_id": "uuid-2",
        "amount": 1000.00,
        "currency": "USD",
        "description": "Portfolio rebalancing"
    }
    """
    data = request.get_json()
    
    source_vault = VaultService.get_vault(data.get('source_vault_id'))
    dest_vault = VaultService.get_vault(data.get('dest_vault_id'))
    
    if not source_vault or not dest_vault:
        return jsonify({'error': 'Vault not found'}), 404
    
    # Verify ownership
    if source_vault.owner_type == 'user' and source_vault.owner_id != current_user.id:
        return jsonify({'error': 'Access denied to source vault'}), 403
    
    if not data.get('amount') or data['amount'] <= 0:
        return jsonify({'error': 'Invalid amount'}), 400
    
    try:
        result = VaultService.transfer_between_vaults(
            source_vault=source_vault,
            dest_vault=dest_vault,
            amount=Decimal(str(data['amount'])),
            currency=data.get('currency', source_vault.base_currency),
            fx_rate=Decimal(str(data['fx_rate'])) if data.get('fx_rate') else None,
            description=data.get('description'),
            created_by=current_user.id
        )
        
        return jsonify({
            'status': 'success',
            'transfer': result
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@vaults_bp.route('/<vault_id>/ledger', methods=['GET'])
@token_required
def get_ledger_history(current_user, vault_id):
    """
    Get ledger transaction history for vault.
    
    Query params:
    - currency: Filter by currency
    - start_date: Start date (ISO format)
    - end_date: End date (ISO format)
    - limit: Max records (default 100)
    """
    vault = VaultService.get_vault(vault_id)
    
    if not vault:
        return jsonify({'error': 'Vault not found'}), 404
    
    if vault.owner_type == 'user' and vault.owner_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    currency = request.args.get('currency')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = int(request.args.get('limit', 100))
    
    # Parse dates
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    if end_date:
        end_date = datetime.fromisoformat(end_date)
    
    history = VaultService.get_ledger_history(
        vault=vault,
        currency=currency,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    
    return jsonify({
        'status': 'success',
        'vault_id': vault_id,
        'history': history
    })


@vaults_bp.route('/<vault_id>/audit', methods=['GET'])
@token_required
def audit_vault(current_user, vault_id):
    """
    Get full audit trail for vault including trial balance.
    """
    vault = VaultService.get_vault(vault_id)
    
    if not vault:
        return jsonify({'error': 'Vault not found'}), 404
    
    if vault.owner_type == 'user' and vault.owner_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Get trial balance for vault accounts
    trial_balance = LedgerService.get_trial_balance(
        entity_type='vault',
        entity_id=vault.id
    )
    
    # Get balances
    balances = VaultService.get_vault_balances(vault)
    
    # Get ledger summary
    summary = LedgerService.get_ledger_summary(
        entity_type='vault',
        entity_id=vault.id
    )
    
    return jsonify({
        'status': 'success',
        'vault': vault.to_dict(),
        'trial_balance': trial_balance,
        'balances': balances,
        'summary': summary
    })


@vaults_bp.route('/<vault_id>/revalue', methods=['POST'])
@token_required
def revalue_positions(current_user, vault_id):
    """
    Trigger FX revaluation for vault positions.
    
    Optional request body:
    {
        "rates": {
            "EUR": 1.08,
            "GBP": 1.27
        }
    }
    """
    vault = VaultService.get_vault(vault_id)
    
    if not vault:
        return jsonify({'error': 'Vault not found'}), 404
    
    if vault.owner_type == 'user' and vault.owner_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json() or {}
    
    # Parse rates if provided
    current_rates = None
    if data.get('rates'):
        current_rates = {
            k: Decimal(str(v)) for k, v in data['rates'].items()
        }
    
    try:
        results = VaultService.revalue_positions(vault, current_rates)
        
        return jsonify({
            'status': 'success',
            'revaluations': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@vaults_bp.route('/<vault_id>/fx-exposure', methods=['GET'])
@token_required
def get_fx_exposure(current_user, vault_id):
    """Get FX exposure report for vault."""
    vault = VaultService.get_vault(vault_id)
    
    if not vault:
        return jsonify({'error': 'Vault not found'}), 404
    
    if vault.owner_type == 'user' and vault.owner_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    exposure = FXService.get_fx_exposure_report(
        entity_type='vault',
        entity_id=vault.id,
        base_currency=vault.base_currency
    )
    
    return jsonify({
        'status': 'success',
        'exposure': exposure
    })


@vaults_bp.route('/<vault_id>/fx-history', methods=['GET'])
@token_required
def get_fx_valuation_history(current_user, vault_id):
    """Get FX valuation snapshot history."""
    vault = VaultService.get_vault(vault_id)
    
    if not vault:
        return jsonify({'error': 'Vault not found'}), 404
    
    if vault.owner_type == 'user' and vault.owner_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    limit = int(request.args.get('limit', 100))
    
    if start_date:
        start_date = datetime.fromisoformat(start_date)
    if end_date:
        end_date = datetime.fromisoformat(end_date)
    
    # Get history for all positions in vault
    history = []
    for position in vault.currency_positions.all():
        pos_history = FXService.get_valuation_history(
            entity_type='vault_position',
            entity_id=position.id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
        history.extend(pos_history)
    
    # Sort by date descending
    history.sort(key=lambda x: x['snapshot_date'], reverse=True)
    
    return jsonify({
        'status': 'success',
        'history': history[:limit]
    })


@vaults_bp.route('/<vault_id>/lock', methods=['POST'])
@token_required
def lock_vault(current_user, vault_id):
    """Lock vault to prevent transactions."""
    vault = VaultService.get_vault(vault_id)
    
    if not vault:
        return jsonify({'error': 'Vault not found'}), 404
    
    if vault.owner_type == 'user' and vault.owner_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    data = request.get_json() or {}
    reason = data.get('reason', 'User requested lock')
    
    VaultService.lock_vault(vault, reason)
    
    return jsonify({
        'status': 'success',
        'message': f'Vault locked: {reason}'
    })


@vaults_bp.route('/<vault_id>/unlock', methods=['POST'])
@token_required
def unlock_vault(current_user, vault_id):
    """Unlock vault."""
    vault = VaultService.get_vault(vault_id)
    
    if not vault:
        return jsonify({'error': 'Vault not found'}), 404
    
    if vault.owner_type == 'user' and vault.owner_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    VaultService.unlock_vault(vault)
    
    return jsonify({
        'status': 'success',
        'message': 'Vault unlocked'
    })


# Ledger auditing endpoints

@vaults_bp.route('/ledger/transaction/<transaction_id>', methods=['GET'])
@token_required
def audit_transaction(current_user, transaction_id):
    """
    Get detailed audit of a specific transaction.
    """
    transaction = LedgerTransaction.query.filter_by(
        transaction_id=transaction_id
    ).first()
    
    if not transaction:
        return jsonify({'error': 'Transaction not found'}), 404
    
    try:
        audit = LedgerService.audit_transaction(transaction.id)
        
        return jsonify({
            'status': 'success',
            'audit': audit
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@vaults_bp.route('/ledger/transaction/<int:transaction_id>/reverse', methods=['POST'])
@token_required
def reverse_transaction(current_user, transaction_id):
    """
    Reverse a ledger transaction.
    
    Request body:
    {
        "reason": "Duplicate entry correction"
    }
    """
    data = request.get_json() or {}
    
    try:
        reversal = LedgerService.reverse_transaction(
            transaction_id=transaction_id,
            reason=data.get('reason'),
            reversed_by=current_user.id
        )
        
        return jsonify({
            'status': 'success',
            'reversal': reversal.to_dict(include_entries=True)
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@vaults_bp.route('/ledger/trial-balance', methods=['GET'])
@token_required
def get_trial_balance(current_user):
    """
    Get trial balance report for user's accounts.
    """
    as_of_date = request.args.get('as_of_date')
    
    if as_of_date:
        as_of_date = datetime.fromisoformat(as_of_date)
    
    trial_balance = LedgerService.get_trial_balance(
        entity_type='user',
        entity_id=current_user.id,
        as_of_date=as_of_date
    )
    
    return jsonify({
        'status': 'success',
        'trial_balance': trial_balance
    })


# FX rate endpoints

@vaults_bp.route('/fx/rates', methods=['GET'])
@token_required
def get_fx_rates(current_user):
    """Get current FX rates."""
    base_currency = request.args.get('base', 'USD')
    
    rates = FXService.get_all_current_rates(base_currency)
    
    return jsonify({
        'status': 'success',
        'base_currency': base_currency,
        'rates': {k: float(v) for k, v in rates.items()}
    })


@vaults_bp.route('/fx/rates', methods=['POST'])
@token_required
def update_fx_rates(current_user):
    """
    Update FX rates (admin only in production).
    
    Request body:
    {
        "rates": [
            {"from_currency": "EUR", "to_currency": "USD", "rate": 1.08},
            {"from_currency": "GBP", "to_currency": "USD", "rate": 1.27}
        ],
        "source": "manual"
    }
    """
    data = request.get_json()
    
    if not data.get('rates'):
        return jsonify({'error': 'Rates array required'}), 400
    
    rates = data['rates']
    source = data.get('source', 'manual')
    
    # Add source to each rate
    for rate in rates:
        rate['source'] = source
    
    count = FXService.store_rates_batch(rates)
    
    return jsonify({
        'status': 'success',
        'rates_updated': count
    })


@vaults_bp.route('/fx/rate/<from_currency>/<to_currency>', methods=['GET'])
@token_required
def get_fx_rate(current_user, from_currency, to_currency):
    """Get specific FX rate."""
    rate_date = request.args.get('date')
    
    if rate_date:
        from datetime import date as date_type
        rate_date = date_type.fromisoformat(rate_date)
    
    rate = FXService.get_rate(
        from_currency.upper(),
        to_currency.upper(),
        rate_date
    )
    
    if not rate:
        return jsonify({'error': 'Rate not found'}), 404
    
    return jsonify({
        'status': 'success',
        'from_currency': from_currency.upper(),
        'to_currency': to_currency.upper(),
        'rate': float(rate)
    })


@vaults_bp.route('/fx/history/<from_currency>/<to_currency>', methods=['GET'])
@token_required
def get_rate_history(current_user, from_currency, to_currency):
    """Get historical FX rates."""
    from datetime import date as date_type, timedelta
    
    end_date = request.args.get('end_date')
    start_date = request.args.get('start_date')
    
    if end_date:
        end_date = date_type.fromisoformat(end_date)
    else:
        end_date = date_type.today()
    
    if start_date:
        start_date = date_type.fromisoformat(start_date)
    else:
        start_date = end_date - timedelta(days=30)
    
    history = FXService.get_rate_history(
        from_currency.upper(),
        to_currency.upper(),
        start_date,
        end_date
    )
    
    return jsonify({
        'status': 'success',
        'from_currency': from_currency.upper(),
        'to_currency': to_currency.upper(),
        'history': history
    })


@vaults_bp.route('/fx/calculate-delta', methods=['POST'])
@token_required
def calculate_fx_delta(current_user):
    """
    Calculate FX delta for a position.
    
    Request body:
    {
        "amount": 10000,
        "original_rate": 1.05,
        "current_rate": 1.08,
        "base_currency": "USD"
    }
    """
    data = request.get_json()
    
    required = ['amount', 'original_rate', 'current_rate']
    for field in required:
        if field not in data:
            return jsonify({'error': f'{field} is required'}), 400
    
    delta = FXService.calculate_fx_delta(
        amount=Decimal(str(data['amount'])),
        original_rate=Decimal(str(data['original_rate'])),
        current_rate=Decimal(str(data['current_rate'])),
        base_currency=data.get('base_currency', 'USD')
    )
    
    return jsonify({
        'status': 'success',
        'delta': delta
    })
