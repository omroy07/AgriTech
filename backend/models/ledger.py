"""
Double-Entry Ledger Models for Multi-Currency Vault Accounting.

This module implements a robust double-entry accounting system with:
- Ledger accounts (assets, liabilities, equity, income, expense)
- Ledger entries with debit/credit legs
- FX valuation snapshots for tracking realized/unrealized gains
- Multi-currency vault support
"""

from datetime import datetime
from decimal import Decimal
from backend.extensions import db
import enum


class AccountType(enum.Enum):
    """Standard accounting account types."""
    ASSET = 'ASSET'
    LIABILITY = 'LIABILITY'
    EQUITY = 'EQUITY'
    INCOME = 'INCOME'
    EXPENSE = 'EXPENSE'


class EntryType(enum.Enum):
    """Type of ledger entry."""
    DEBIT = 'DEBIT'
    CREDIT = 'CREDIT'


class TransactionType(enum.Enum):
    """Types of financial transactions."""
    DEPOSIT = 'DEPOSIT'
    WITHDRAWAL = 'WITHDRAWAL'
    TRANSFER = 'TRANSFER'
    FX_REVALUATION = 'FX_REVALUATION'
    FX_REALIZED_GAIN = 'FX_REALIZED_GAIN'
    FX_UNREALIZED_GAIN = 'FX_UNREALIZED_GAIN'
    CARBON_CREDIT_MINT = 'CARBON_CREDIT_MINT'    # New credit minted from sequestration
    CARBON_CREDIT_SALE = 'CARBON_CREDIT_SALE'    # Credit sold to ESG buyer
    FREIGHT_ESCROW_HOLD = 'FREIGHT_ESCROW_HOLD'  # Funds locked into freight escrow
    FREIGHT_RELEASE = 'FREIGHT_RELEASE'          # Smart-contract release on geo-fence confirm
    DIVIDEND = 'DIVIDEND'
    FEE = 'FEE'
    INTEREST = 'INTEREST'
    ARBITRAGE_EXECUTION = 'ARBITRAGE_EXECUTION'  # Auto-execution of quant arbitrage trade
    CARBON_CREDIT_MINT = 'CARBON_CREDIT_MINT'    # New credit minted from sequestration
    CARBON_CREDIT_SALE = 'CARBON_CREDIT_SALE'    # Credit sold to ESG buyer


class LedgerAccount(db.Model):
    """
    Chart of Accounts for double-entry bookkeeping.
    
    Each account represents a specific category in the accounting system.
    Accounts are hierarchical with parent-child relationships.
    """
    __tablename__ = 'ledger_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    account_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    account_type = db.Column(db.Enum(AccountType), nullable=False)
    currency = db.Column(db.String(3), default='USD', nullable=False)
    
    # Hierarchical structure
    parent_id = db.Column(db.Integer, db.ForeignKey('ledger_accounts.id'), nullable=True)
    parent = db.relationship('LedgerAccount', remote_side=[id], backref='children')
    
    # Associated entity (farm, user, vault)
    entity_type = db.Column(db.String(50), nullable=True)  # 'farm', 'user', 'vault'
    entity_id = db.Column(db.Integer, nullable=True)
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_system = db.Column(db.Boolean, default=False)  # System accounts can't be deleted
    
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    entries = db.relationship('LedgerEntry', back_populates='account', lazy='dynamic')
    
    __table_args__ = (
        db.Index('idx_ledger_account_entity', 'entity_type', 'entity_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_code': self.account_code,
            'name': self.name,
            'account_type': self.account_type.value,
            'currency': self.currency,
            'parent_id': self.parent_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'is_active': self.is_active,
            'is_system': self.is_system,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_balance(self, as_of_date=None):
        """
        Calculate account balance from ledger entries.
        
        For ASSET and EXPENSE accounts: Debits increase, Credits decrease
        For LIABILITY, EQUITY, INCOME accounts: Credits increase, Debits decrease
        """
        from sqlalchemy import func
        
        query = LedgerEntry.query.filter_by(account_id=self.id)
        
        if as_of_date:
            query = query.filter(LedgerEntry.entry_date <= as_of_date)
        
        debits = query.filter_by(entry_type=EntryType.DEBIT).with_entities(
            func.coalesce(func.sum(LedgerEntry.amount), 0)
        ).scalar() or Decimal('0')
        
        credits = query.filter_by(entry_type=EntryType.CREDIT).with_entities(
            func.coalesce(func.sum(LedgerEntry.amount), 0)
        ).scalar() or Decimal('0')
        
        if self.account_type in [AccountType.ASSET, AccountType.EXPENSE]:
            return Decimal(str(debits)) - Decimal(str(credits))
        else:
            return Decimal(str(credits)) - Decimal(str(debits))


class LedgerTransaction(db.Model):
    """
    Groups related ledger entries into a single atomic transaction.
    
    Every transaction must have balanced debits and credits.
    """
    __tablename__ = 'ledger_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    transaction_type = db.Column(db.Enum(TransactionType), nullable=False)
    
    # Reference to source operation
    source_type = db.Column(db.String(50), nullable=True)  # 'vault_transfer', 'investment', etc.
    source_id = db.Column(db.Integer, nullable=True)
    
    # Transaction metadata
    description = db.Column(db.Text, nullable=True)
    reference_number = db.Column(db.String(100), nullable=True)
    
    # Multi-currency support
    base_currency = db.Column(db.String(3), default='USD', nullable=False)
    base_amount = db.Column(db.Numeric(18, 6), nullable=False)  # Amount in base currency
    
    # FX information
    fx_rate_used = db.Column(db.Numeric(18, 8), nullable=True)
    fx_rate_date = db.Column(db.DateTime, nullable=True)
    
    # Audit trail
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    is_reversed = db.Column(db.Boolean, default=False)
    reversed_by_id = db.Column(db.Integer, db.ForeignKey('ledger_transactions.id'), nullable=True)
    
    # Relationships
    entries = db.relationship('LedgerEntry', back_populates='transaction', lazy='dynamic')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    __table_args__ = (
        db.Index('idx_ledger_txn_source', 'source_type', 'source_id'),
        db.Index('idx_ledger_txn_date', 'created_at'),
    )
    
    def to_dict(self, include_entries=False):
        result = {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'transaction_type': self.transaction_type.value,
            'source_type': self.source_type,
            'source_id': self.source_id,
            'description': self.description,
            'reference_number': self.reference_number,
            'base_currency': self.base_currency,
            'base_amount': float(self.base_amount),
            'fx_rate_used': float(self.fx_rate_used) if self.fx_rate_used else None,
            'fx_rate_date': self.fx_rate_date.isoformat() if self.fx_rate_date else None,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_reversed': self.is_reversed
        }
        
        if include_entries:
            result['entries'] = [e.to_dict() for e in self.entries.all()]
        
        return result
    
    def is_balanced(self):
        """Verify that total debits equal total credits."""
        from sqlalchemy import func
        
        debits = self.entries.filter_by(entry_type=EntryType.DEBIT).with_entities(
            func.coalesce(func.sum(LedgerEntry.base_amount), 0)
        ).scalar() or Decimal('0')
        
        credits = self.entries.filter_by(entry_type=EntryType.CREDIT).with_entities(
            func.coalesce(func.sum(LedgerEntry.base_amount), 0)
        ).scalar() or Decimal('0')
        
        return abs(Decimal(str(debits)) - Decimal(str(credits))) < Decimal('0.01')


class LedgerEntry(db.Model):
    """
    Individual debit or credit leg of a double-entry transaction.
    
    Every entry belongs to a transaction and affects a single account.
    """
    __tablename__ = 'ledger_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('ledger_transactions.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('ledger_accounts.id'), nullable=False)
    
    entry_type = db.Column(db.Enum(EntryType), nullable=False)
    
    # Original currency amount
    amount = db.Column(db.Numeric(18, 6), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    
    # Base currency equivalent (for reporting)
    base_amount = db.Column(db.Numeric(18, 6), nullable=False)
    base_currency = db.Column(db.String(3), default='USD', nullable=False)
    fx_rate = db.Column(db.Numeric(18, 8), nullable=True)
    
    # Entry date (can differ from transaction creation for backdating)
    entry_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Memo and metadata
    memo = db.Column(db.String(500), nullable=True)
    metadata_json = db.Column(db.JSON, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    transaction = db.relationship('LedgerTransaction', back_populates='entries')
    account = db.relationship('LedgerAccount', back_populates='entries')
    
    __table_args__ = (
        db.Index('idx_ledger_entry_account_date', 'account_id', 'entry_date'),
        db.Index('idx_ledger_entry_txn', 'transaction_id'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'transaction_id': self.transaction_id,
            'account_id': self.account_id,
            'account_code': self.account.account_code if self.account else None,
            'account_name': self.account.name if self.account else None,
            'entry_type': self.entry_type.value,
            'amount': float(self.amount),
            'currency': self.currency,
            'base_amount': float(self.base_amount),
            'base_currency': self.base_currency,
            'fx_rate': float(self.fx_rate) if self.fx_rate else None,
            'entry_date': self.entry_date.isoformat() if self.entry_date else None,
            'memo': self.memo
        }


class FXValuationSnapshot(db.Model):
    """
    Point-in-time FX valuation for multi-currency positions.
    
    Tracks unrealized gains/losses from currency movements.
    """
    __tablename__ = 'fx_valuation_snapshots'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Entity being valued (vault, account, portfolio)
    entity_type = db.Column(db.String(50), nullable=False)
    entity_id = db.Column(db.Integer, nullable=False)
    
    # Snapshot timing
    snapshot_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Position details
    currency = db.Column(db.String(3), nullable=False)
    position_amount = db.Column(db.Numeric(18, 6), nullable=False)
    
    # FX rates
    original_fx_rate = db.Column(db.Numeric(18, 8), nullable=False)
    current_fx_rate = db.Column(db.Numeric(18, 8), nullable=False)
    
    # Base currency values
    base_currency = db.Column(db.String(3), default='USD', nullable=False)
    original_base_value = db.Column(db.Numeric(18, 6), nullable=False)
    current_base_value = db.Column(db.Numeric(18, 6), nullable=False)
    
    # Gain/Loss calculation
    unrealized_gain_loss = db.Column(db.Numeric(18, 6), nullable=False)
    unrealized_gain_loss_pct = db.Column(db.Numeric(10, 4), nullable=True)
    
    # Period tracking
    period_start = db.Column(db.DateTime, nullable=True)
    period_end = db.Column(db.DateTime, nullable=True)
    
    # Running totals
    cumulative_realized_gain = db.Column(db.Numeric(18, 6), default=0)
    cumulative_unrealized_gain = db.Column(db.Numeric(18, 6), default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_fx_snapshot_entity', 'entity_type', 'entity_id'),
        db.Index('idx_fx_snapshot_date', 'snapshot_date'),
        db.Index('idx_fx_snapshot_currency', 'currency'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'snapshot_date': self.snapshot_date.isoformat() if self.snapshot_date else None,
            'currency': self.currency,
            'position_amount': float(self.position_amount),
            'original_fx_rate': float(self.original_fx_rate),
            'current_fx_rate': float(self.current_fx_rate),
            'base_currency': self.base_currency,
            'original_base_value': float(self.original_base_value),
            'current_base_value': float(self.current_base_value),
            'unrealized_gain_loss': float(self.unrealized_gain_loss),
            'unrealized_gain_loss_pct': float(self.unrealized_gain_loss_pct) if self.unrealized_gain_loss_pct else None,
            'cumulative_realized_gain': float(self.cumulative_realized_gain),
            'cumulative_unrealized_gain': float(self.cumulative_unrealized_gain),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Vault(db.Model):
    """
    Multi-currency vault for holding funds and investments.
    
    Balances are reconstructed from ledger entries, not stored directly.
    """
    __tablename__ = 'vaults'
    
    id = db.Column(db.Integer, primary_key=True)
    vault_id = db.Column(db.String(36), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    
    # Owner
    owner_type = db.Column(db.String(50), nullable=False)  # 'user', 'farm', 'organization'
    owner_id = db.Column(db.Integer, nullable=False)
    
    # Primary currency for reporting
    base_currency = db.Column(db.String(3), default='USD', nullable=False)
    
    # Associated ledger account
    ledger_account_id = db.Column(db.Integer, db.ForeignKey('ledger_accounts.id'), nullable=True)
    ledger_account = db.relationship('LedgerAccount', foreign_keys=[ledger_account_id])
    
    # Vault configuration
    allow_multi_currency = db.Column(db.Boolean, default=True)
    auto_fx_revaluation = db.Column(db.Boolean, default=True)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_locked = db.Column(db.Boolean, default=False)
    locked_reason = db.Column(db.String(200), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    currency_positions = db.relationship('VaultCurrencyPosition', back_populates='vault', lazy='dynamic')
    
    __table_args__ = (
        db.Index('idx_vault_owner', 'owner_type', 'owner_id'),
    )
    
    def to_dict(self, include_positions=False):
        result = {
            'id': self.id,
            'vault_id': self.vault_id,
            'name': self.name,
            'owner_type': self.owner_type,
            'owner_id': self.owner_id,
            'base_currency': self.base_currency,
            'ledger_account_id': self.ledger_account_id,
            'allow_multi_currency': self.allow_multi_currency,
            'auto_fx_revaluation': self.auto_fx_revaluation,
            'is_active': self.is_active,
            'is_locked': self.is_locked,
            'locked_reason': self.locked_reason,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        if include_positions:
            result['positions'] = [p.to_dict() for p in self.currency_positions.all()]
        
        return result


class VaultCurrencyPosition(db.Model):
    """
    Tracks currency positions within a vault.
    
    The balance is derived from ledger entries; this table provides
    quick access to position metadata and FX tracking.
    """
    __tablename__ = 'vault_currency_positions'
    
    id = db.Column(db.Integer, primary_key=True)
    vault_id = db.Column(db.Integer, db.ForeignKey('vaults.id'), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    
    # Associated ledger sub-account for this currency
    ledger_account_id = db.Column(db.Integer, db.ForeignKey('ledger_accounts.id'), nullable=True)
    ledger_account = db.relationship('LedgerAccount', foreign_keys=[ledger_account_id])
    
    # Cost basis tracking for FX gains
    cost_basis_rate = db.Column(db.Numeric(18, 8), nullable=True)  # Weighted average rate
    cost_basis_amount = db.Column(db.Numeric(18, 6), nullable=True)  # Total cost in base currency
    
    # Last revaluation
    last_fx_rate = db.Column(db.Numeric(18, 8), nullable=True)
    last_revaluation_date = db.Column(db.DateTime, nullable=True)
    
    # Cumulative FX gains/losses
    cumulative_realized_fx_gain = db.Column(db.Numeric(18, 6), default=0)
    cumulative_unrealized_fx_gain = db.Column(db.Numeric(18, 6), default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vault = db.relationship('Vault', back_populates='currency_positions')
    
    __table_args__ = (
        db.UniqueConstraint('vault_id', 'currency', name='uq_vault_currency'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'vault_id': self.vault_id,
            'currency': self.currency,
            'ledger_account_id': self.ledger_account_id,
            'cost_basis_rate': float(self.cost_basis_rate) if self.cost_basis_rate else None,
            'cost_basis_amount': float(self.cost_basis_amount) if self.cost_basis_amount else None,
            'last_fx_rate': float(self.last_fx_rate) if self.last_fx_rate else None,
            'last_revaluation_date': self.last_revaluation_date.isoformat() if self.last_revaluation_date else None,
            'cumulative_realized_fx_gain': float(self.cumulative_realized_fx_gain),
            'cumulative_unrealized_fx_gain': float(self.cumulative_unrealized_fx_gain),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class FXRate(db.Model):
    """
    Historical and current FX rates.
    """
    __tablename__ = 'fx_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    from_currency = db.Column(db.String(3), nullable=False)
    to_currency = db.Column(db.String(3), nullable=False)
    rate = db.Column(db.Numeric(18, 8), nullable=False)
    rate_date = db.Column(db.Date, nullable=False)
    rate_time = db.Column(db.DateTime, default=datetime.utcnow)
    source = db.Column(db.String(50), nullable=True)  # 'ECB', 'FOREX', etc.
    is_current = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.Index('idx_fx_rate_pair', 'from_currency', 'to_currency'),
        db.Index('idx_fx_rate_date', 'rate_date'),
        db.UniqueConstraint('from_currency', 'to_currency', 'rate_date', name='uq_fx_rate_daily'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'from_currency': self.from_currency,
            'to_currency': self.to_currency,
            'rate': float(self.rate),
            'rate_date': self.rate_date.isoformat() if self.rate_date else None,
            'source': self.source,
            'is_current': self.is_current
        }
