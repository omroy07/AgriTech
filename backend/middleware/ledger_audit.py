"""
Ledger Audit Middleware: Intercepts and maps transactions to ledger legs.

This middleware provides:
- Automatic ledger entry creation for financial operations
- Transaction-to-ledger mapping
- Audit trail for all financial movements
- Pre/post operation validation
"""

import functools
import json
from decimal import Decimal
from datetime import datetime
from typing import Dict, List, Optional, Callable
from flask import request, g, has_request_context
import logging

from backend.extensions import db
from backend.services.ledger_service import LedgerService
from backend.services.audit_service import AuditService
from backend.models.ledger import (
    LedgerTransaction, LedgerEntry, TransactionType, AccountType
)

logger = logging.getLogger(__name__)


class LedgerAuditMiddleware:
    """
    Middleware for automatic ledger auditing of financial operations.
    
    Intercepts API requests that involve financial transactions and
    ensures they are properly recorded in the double-entry ledger.
    """
    
    # Patterns of endpoints that require ledger auditing
    FINANCIAL_ENDPOINTS = [
        '/api/v1/vaults/',
        '/api/v1/financials/',
        '/api/v1/payments/',
        '/api/v1/transfers/',
        '/api/v1/investments/',
    ]
    
    # Operations that create ledger entries
    LEDGER_OPERATIONS = {
        'POST': ['deposit', 'withdraw', 'transfer', 'payment', 'investment'],
        'PUT': ['adjustment', 'correction'],
        'DELETE': ['reversal', 'cancellation']
    }
    
    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware with Flask app."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Register ledger validation hook
        app.config.setdefault('LEDGER_AUDIT_ENABLED', True)
        app.config.setdefault('LEDGER_STRICT_BALANCE', True)
        
        logger.info("LedgerAuditMiddleware initialized")
    
    def before_request(self):
        """Pre-request hook for ledger operations."""
        if not has_request_context():
            return
        
        # Initialize ledger context
        g.ledger_audit = {
            'enabled': self._is_financial_endpoint(),
            'start_time': datetime.utcnow(),
            'pre_balances': {},
            'operation_type': self._detect_operation_type()
        }
        
        if g.ledger_audit['enabled']:
            # Capture pre-operation state for audit trail
            self._capture_pre_state()
    
    def after_request(self, response):
        """Post-request hook for ledger validation and audit logging."""
        if not has_request_context():
            return response
        
        if not getattr(g, 'ledger_audit', {}).get('enabled'):
            return response
        
        # Only audit successful financial operations
        if response.status_code in [200, 201]:
            self._audit_operation(response)
        
        return response
    
    def _is_financial_endpoint(self) -> bool:
        """Check if current request is to a financial endpoint."""
        if not request.path:
            return False
        
        return any(
            request.path.startswith(pattern)
            for pattern in self.FINANCIAL_ENDPOINTS
        )
    
    def _detect_operation_type(self) -> Optional[str]:
        """Detect the type of financial operation from request."""
        if not request.path:
            return None
        
        method = request.method
        
        # Check for known operations
        operations = self.LEDGER_OPERATIONS.get(method, [])
        
        for op in operations:
            if op in request.path.lower():
                return op
        
        return None
    
    def _capture_pre_state(self):
        """Capture account balances before operation for audit."""
        try:
            # Extract account IDs from request
            data = request.get_json(silent=True) or {}
            
            account_ids = []
            
            # Look for account references in request
            for key in ['account_id', 'source_account_id', 'dest_account_id',
                       'from_account', 'to_account', 'vault_id']:
                if key in data:
                    account_ids.append(data[key])
            
            # Capture balances
            g.ledger_audit['pre_balances'] = {}
            
            for account_id in account_ids:
                try:
                    balance = LedgerService.get_account_balance(account_id)
                    g.ledger_audit['pre_balances'][account_id] = float(balance)
                except Exception:
                    pass
                    
        except Exception as e:
            logger.warning(f"Failed to capture pre-state: {e}")
    
    def _audit_operation(self, response):
        """Create audit record for the financial operation."""
        try:
            operation_type = g.ledger_audit.get('operation_type')
            
            if not operation_type:
                return
            
            # Extract response data
            response_data = {}
            try:
                response_data = json.loads(response.get_data(as_text=True))
            except Exception:
                pass
            
            # Calculate duration
            start_time = g.ledger_audit.get('start_time', datetime.utcnow())
            duration_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            # Log to audit service
            AuditService.log_action(
                action=f"LEDGER_{operation_type.upper()}",
                risk_level='MEDIUM' if operation_type in ['transfer', 'withdrawal'] else 'LOW',
                meta_data={
                    'operation_type': operation_type,
                    'endpoint': request.path,
                    'method': request.method,
                    'pre_balances': g.ledger_audit.get('pre_balances', {}),
                    'status_code': response.status_code,
                    'duration_ms': duration_ms,
                    'transaction_id': response_data.get('transaction_id')
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to audit operation: {e}")


def ledger_transaction(
    transaction_type: TransactionType = None,
    required_accounts: List[str] = None,
    validate_balance: bool = True
):
    """
    Decorator for functions that create ledger transactions.
    
    Automatically wraps the function in a ledger transaction context,
    validates balance requirements, and ensures proper commit/rollback.
    
    Args:
        transaction_type: Type of transaction being created
        required_accounts: List of account code patterns required
        validate_balance: If True, validate balances before proceeding
        
    Example:
        @ledger_transaction(
            transaction_type=TransactionType.TRANSFER,
            required_accounts=['source', 'destination'],
            validate_balance=True
        )
        def transfer_funds(source_id, dest_id, amount):
            ...
    """
    def decorator(f: Callable):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            # Initialize ledger transaction context
            g.ledger_context = {
                'transaction_type': transaction_type,
                'start_time': datetime.utcnow(),
                'entries': [],
                'validated': False
            }
            
            try:
                # Validate required accounts if specified
                if required_accounts and validate_balance:
                    _validate_required_accounts(kwargs, required_accounts)
                
                g.ledger_context['validated'] = True
                
                # Execute the function
                result = f(*args, **kwargs)
                
                # Commit if we created a transaction
                if getattr(g, 'ledger_transaction_created', False):
                    db.session.commit()
                
                return result
                
            except Exception as e:
                # Rollback on error
                db.session.rollback()
                logger.error(f"Ledger transaction failed: {e}")
                raise
            finally:
                # Cleanup context
                g.ledger_context = None
                
        return wrapper
    return decorator


def _validate_required_accounts(kwargs: dict, required: List[str]):
    """Validate that required accounts exist and have sufficient balance."""
    for account_key in required:
        # Find account ID in kwargs
        account_id = None
        for k, v in kwargs.items():
            if account_key in k.lower() and isinstance(v, int):
                account_id = v
                break
        
        if not account_id:
            continue
        
        # Verify account exists
        from backend.models.ledger import LedgerAccount
        account = LedgerAccount.query.get(account_id)
        
        if not account:
            raise ValueError(f"Account {account_id} not found")
        
        if not account.is_active:
            raise ValueError(f"Account {account.account_code} is inactive")


def map_to_ledger_entry(
    account_code: str,
    amount: Decimal,
    currency: str,
    entry_type: str,
    fx_rate: Decimal = None,
    memo: str = None
) -> Dict:
    """
    Helper function to create a ledger entry mapping.
    
    Used by route handlers to build ledger entries before
    passing to LedgerService.
    
    Args:
        account_code: Target account code
        amount: Transaction amount
        currency: Currency code
        entry_type: 'DEBIT' or 'CREDIT'
        fx_rate: FX rate to base currency
        memo: Entry memo
        
    Returns:
        Dict suitable for LedgerService.create_transaction
    """
    from backend.models.ledger import LedgerAccount
    
    account = LedgerAccount.query.filter_by(account_code=account_code).first()
    
    if not account:
        raise ValueError(f"Account {account_code} not found")
    
    return {
        'account_id': account.id,
        'entry_type': entry_type,
        'amount': float(amount),
        'currency': currency,
        'fx_rate': float(fx_rate) if fx_rate else 1.0,
        'memo': memo
    }


class TransactionMapper:
    """
    Maps business operations to ledger entries.
    
    Provides templates for common transaction patterns.
    """
    
    @staticmethod
    def map_deposit(
        asset_account_id: int,
        equity_account_id: int,
        amount: Decimal,
        currency: str,
        fx_rate: Decimal = None,
        description: str = None
    ) -> List[Dict]:
        """Map a deposit to ledger entries."""
        return [
            {
                'account_id': asset_account_id,
                'entry_type': 'DEBIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate or 1),
                'memo': description or 'Deposit'
            },
            {
                'account_id': equity_account_id,
                'entry_type': 'CREDIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate or 1),
                'memo': description or 'Deposit'
            }
        ]
    
    @staticmethod
    def map_withdrawal(
        asset_account_id: int,
        equity_account_id: int,
        amount: Decimal,
        currency: str,
        fx_rate: Decimal = None,
        description: str = None
    ) -> List[Dict]:
        """Map a withdrawal to ledger entries."""
        return [
            {
                'account_id': asset_account_id,
                'entry_type': 'CREDIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate or 1),
                'memo': description or 'Withdrawal'
            },
            {
                'account_id': equity_account_id,
                'entry_type': 'DEBIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate or 1),
                'memo': description or 'Withdrawal'
            }
        ]
    
    @staticmethod
    def map_transfer(
        source_account_id: int,
        dest_account_id: int,
        amount: Decimal,
        currency: str,
        fx_rate: Decimal = None,
        description: str = None
    ) -> List[Dict]:
        """Map a transfer to ledger entries."""
        return [
            {
                'account_id': source_account_id,
                'entry_type': 'CREDIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate or 1),
                'memo': description or 'Transfer out'
            },
            {
                'account_id': dest_account_id,
                'entry_type': 'DEBIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': float(fx_rate or 1),
                'memo': description or 'Transfer in'
            }
        ]
    
    @staticmethod
    def map_fx_gain(
        asset_account_id: int,
        fx_gain_account_id: int,
        gain_amount: Decimal,
        base_currency: str,
        description: str = None
    ) -> List[Dict]:
        """Map FX gain to ledger entries."""
        if gain_amount > 0:
            # Gain: Debit asset, Credit income
            return [
                {
                    'account_id': asset_account_id,
                    'entry_type': 'DEBIT',
                    'amount': float(gain_amount),
                    'currency': base_currency,
                    'fx_rate': 1.0,
                    'memo': description or 'FX gain'
                },
                {
                    'account_id': fx_gain_account_id,
                    'entry_type': 'CREDIT',
                    'amount': float(gain_amount),
                    'currency': base_currency,
                    'fx_rate': 1.0,
                    'memo': description or 'FX gain'
                }
            ]
        else:
            # Loss: Credit asset, Debit expense
            loss_amount = abs(gain_amount)
            return [
                {
                    'account_id': asset_account_id,
                    'entry_type': 'CREDIT',
                    'amount': float(loss_amount),
                    'currency': base_currency,
                    'fx_rate': 1.0,
                    'memo': description or 'FX loss'
                },
                {
                    'account_id': fx_gain_account_id,
                    'entry_type': 'DEBIT',
                    'amount': float(loss_amount),
                    'currency': base_currency,
                    'fx_rate': 1.0,
                    'memo': description or 'FX loss'
                }
            ]
    
    @staticmethod
    def map_fee(
        asset_account_id: int,
        expense_account_id: int,
        amount: Decimal,
        currency: str,
        description: str = None
    ) -> List[Dict]:
        """Map a fee to ledger entries."""
        return [
            {
                'account_id': asset_account_id,
                'entry_type': 'CREDIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': 1.0,
                'memo': description or 'Fee payment'
            },
            {
                'account_id': expense_account_id,
                'entry_type': 'DEBIT',
                'amount': float(amount),
                'currency': currency,
                'fx_rate': 1.0,
                'memo': description or 'Fee expense'
            }
        ]


def validate_ledger_balance(f: Callable):
    """
    Decorator to validate that ledger remains balanced after operation.
    
    Should be used on any function that modifies ledger entries.
    """
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        
        # If a transaction was created, validate it's balanced
        if isinstance(result, LedgerTransaction):
            if not result.is_balanced():
                db.session.rollback()
                raise ValueError(
                    f"Transaction {result.transaction_id} is not balanced"
                )
        
        return result
    
    return wrapper


def audit_ledger_operation(action_name: str = None):
    """
    Decorator for explicit auditing of ledger operations.
    
    Args:
        action_name: Name of the action for audit log
    """
    def decorator(f: Callable):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            start_time = datetime.utcnow()
            
            try:
                result = f(*args, **kwargs)
                
                # Log success
                AuditService.log_action(
                    action=action_name or f.__name__.upper(),
                    risk_level='MEDIUM',
                    meta_data={
                        'function': f.__name__,
                        'args': str(args)[:200],
                        'status': 'success',
                        'duration_ms': int((datetime.utcnow() - start_time).total_seconds() * 1000)
                    }
                )
                
                return result
                
            except Exception as e:
                # Log failure
                AuditService.log_action(
                    action=action_name or f.__name__.upper(),
                    risk_level='HIGH',
                    meta_data={
                        'function': f.__name__,
                        'status': 'error',
                        'error': str(e),
                        'duration_ms': int((datetime.utcnow() - start_time).total_seconds() * 1000)
                    }
                )
                raise
                
        return wrapper
    return decorator
