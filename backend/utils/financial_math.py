"""
Financial Math Utilities: Base-currency normalization and financial calculations.

This module provides:
- Currency normalization formulas
- FX conversion utilities
- Financial precision handling
- Gain/loss calculations
- Cost basis methods (FIFO, LIFO, weighted average)
"""

from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN, ROUND_UP, InvalidOperation
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


# Precision constants
CURRENCY_PRECISION = Decimal('0.01')        # 2 decimal places for currency
RATE_PRECISION = Decimal('0.00000001')      # 8 decimal places for FX rates
PERCENTAGE_PRECISION = Decimal('0.0001')    # 4 decimal places for percentages
INTERNAL_PRECISION = Decimal('0.000001')    # 6 decimal places for internal calcs


@dataclass
class NormalizedAmount:
    """Represents an amount normalized to base currency."""
    original_amount: Decimal
    original_currency: str
    base_amount: Decimal
    base_currency: str
    fx_rate: Decimal
    rate_date: date
    
    def to_dict(self) -> Dict:
        return {
            'original_amount': float(self.original_amount),
            'original_currency': self.original_currency,
            'base_amount': float(self.base_amount),
            'base_currency': self.base_currency,
            'fx_rate': float(self.fx_rate),
            'rate_date': self.rate_date.isoformat()
        }


def normalize_to_base_currency(
    amount: Union[Decimal, float, str],
    currency: str,
    base_currency: str = 'USD',
    fx_rate: Union[Decimal, float] = None,
    rate_date: date = None
) -> NormalizedAmount:
    """
    Normalize an amount to base currency.
    
    Args:
        amount: Amount in original currency
        currency: Original currency code
        base_currency: Target base currency
        fx_rate: FX rate (1 currency = fx_rate base_currency)
        rate_date: Date of FX rate
        
    Returns:
        NormalizedAmount with original and base values
    """
    amount = to_decimal(amount)
    rate_date = rate_date or date.today()
    
    if currency == base_currency:
        return NormalizedAmount(
            original_amount=amount,
            original_currency=currency,
            base_amount=amount,
            base_currency=base_currency,
            fx_rate=Decimal('1'),
            rate_date=rate_date
        )
    
    # Get rate if not provided
    if fx_rate is None:
        from backend.services.fx_service import FXService
        fx_rate = FXService.get_rate(currency, base_currency, rate_date)
        
        if fx_rate is None:
            raise ValueError(f"No FX rate available for {currency}/{base_currency}")
    
    fx_rate = to_decimal(fx_rate)
    base_amount = (amount * fx_rate).quantize(INTERNAL_PRECISION, rounding=ROUND_HALF_UP)
    
    return NormalizedAmount(
        original_amount=amount,
        original_currency=currency,
        base_amount=base_amount,
        base_currency=base_currency,
        fx_rate=fx_rate,
        rate_date=rate_date
    )


def to_decimal(value: Union[Decimal, float, str, int, None]) -> Decimal:
    """
    Safely convert a value to Decimal.
    
    Args:
        value: Value to convert
        
    Returns:
        Decimal representation
    """
    if value is None:
        return Decimal('0')
    
    if isinstance(value, Decimal):
        return value
    
    try:
        return Decimal(str(value))
    except InvalidOperation:
        logger.error(f"Invalid decimal conversion: {value}")
        return Decimal('0')


def round_currency(amount: Decimal, precision: Decimal = CURRENCY_PRECISION) -> Decimal:
    """
    Round amount to currency precision.
    
    Uses banker's rounding (ROUND_HALF_UP).
    """
    return amount.quantize(precision, rounding=ROUND_HALF_UP)


def round_rate(rate: Decimal) -> Decimal:
    """Round FX rate to standard precision."""
    return rate.quantize(RATE_PRECISION, rounding=ROUND_HALF_UP)


def calculate_fx_delta(
    position_amount: Decimal,
    original_rate: Decimal,
    current_rate: Decimal,
    base_currency: str = 'USD'
) -> Dict:
    """
    Calculate FX gain/loss delta for a position.
    
    Args:
        position_amount: Amount in foreign currency
        original_rate: Rate when position was acquired
        current_rate: Current FX rate
        base_currency: Base currency for reporting
        
    Returns:
        Dict with delta calculations
    """
    position_amount = to_decimal(position_amount)
    original_rate = to_decimal(original_rate)
    current_rate = to_decimal(current_rate)
    
    original_value = round_currency(position_amount * original_rate)
    current_value = round_currency(position_amount * current_rate)
    delta = current_value - original_value
    
    delta_pct = Decimal('0')
    if original_value != 0:
        delta_pct = (delta / original_value * 100).quantize(
            PERCENTAGE_PRECISION, rounding=ROUND_HALF_UP
        )
    
    return {
        'position_amount': float(position_amount),
        'original_rate': float(original_rate),
        'current_rate': float(current_rate),
        'original_value': float(original_value),
        'current_value': float(current_value),
        'delta': float(delta),
        'delta_pct': float(delta_pct),
        'base_currency': base_currency,
        'is_gain': delta > 0
    }


def calculate_realized_fx_gain(
    amount_sold: Decimal,
    cost_basis_rate: Decimal,
    sale_rate: Decimal
) -> Decimal:
    """
    Calculate realized FX gain/loss on currency sale.
    
    Args:
        amount_sold: Amount of foreign currency sold
        cost_basis_rate: Weighted average rate at acquisition
        sale_rate: Rate at time of sale
        
    Returns:
        Realized gain (positive) or loss (negative)
    """
    amount_sold = to_decimal(amount_sold)
    cost_basis_rate = to_decimal(cost_basis_rate)
    sale_rate = to_decimal(sale_rate)
    
    cost_basis_value = amount_sold * cost_basis_rate
    sale_value = amount_sold * sale_rate
    
    return round_currency(sale_value - cost_basis_value)


def calculate_weighted_average_rate(
    existing_amount: Decimal,
    existing_rate: Decimal,
    new_amount: Decimal,
    new_rate: Decimal
) -> Decimal:
    """
    Calculate weighted average FX rate after adding to position.
    
    Args:
        existing_amount: Current position amount
        existing_rate: Current weighted average rate
        new_amount: Amount being added
        new_rate: Rate for new amount
        
    Returns:
        New weighted average rate
    """
    existing_amount = to_decimal(existing_amount)
    existing_rate = to_decimal(existing_rate)
    new_amount = to_decimal(new_amount)
    new_rate = to_decimal(new_rate)
    
    if existing_amount <= 0:
        return new_rate
    
    total_amount = existing_amount + new_amount
    if total_amount <= 0:
        return new_rate
    
    existing_value = existing_amount * existing_rate
    new_value = new_amount * new_rate
    total_value = existing_value + new_value
    
    return round_rate(total_value / total_amount)


class CostBasisCalculator:
    """
    Calculates cost basis using different methods.
    
    Supports:
    - FIFO (First In, First Out)
    - LIFO (Last In, First Out)
    - Weighted Average
    - Specific Identification
    """
    
    @staticmethod
    def fifo_cost_basis(
        lots: List[Dict],
        amount_to_sell: Decimal
    ) -> Tuple[Decimal, List[Dict]]:
        """
        Calculate cost basis using FIFO method.
        
        Args:
            lots: List of purchase lots [{'amount': x, 'rate': y, 'date': z}]
            amount_to_sell: Amount to calculate basis for
            
        Returns:
            Tuple of (cost_basis, remaining_lots)
        """
        amount_to_sell = to_decimal(amount_to_sell)
        
        # Sort by date ascending (oldest first)
        sorted_lots = sorted(lots, key=lambda x: x.get('date', date.min))
        
        total_cost = Decimal('0')
        remaining = amount_to_sell
        remaining_lots = []
        
        for lot in sorted_lots:
            lot_amount = to_decimal(lot['amount'])
            lot_rate = to_decimal(lot['rate'])
            
            if remaining <= 0:
                remaining_lots.append(lot)
                continue
            
            if lot_amount <= remaining:
                # Use entire lot
                total_cost += lot_amount * lot_rate
                remaining -= lot_amount
            else:
                # Partial lot usage
                total_cost += remaining * lot_rate
                remaining_lots.append({
                    **lot,
                    'amount': float(lot_amount - remaining)
                })
                remaining = Decimal('0')
        
        avg_rate = total_cost / amount_to_sell if amount_to_sell > 0 else Decimal('0')
        
        return round_currency(total_cost), remaining_lots
    
    @staticmethod
    def lifo_cost_basis(
        lots: List[Dict],
        amount_to_sell: Decimal
    ) -> Tuple[Decimal, List[Dict]]:
        """
        Calculate cost basis using LIFO method.
        
        Args:
            lots: List of purchase lots
            amount_to_sell: Amount to calculate basis for
            
        Returns:
            Tuple of (cost_basis, remaining_lots)
        """
        amount_to_sell = to_decimal(amount_to_sell)
        
        # Sort by date descending (newest first)
        sorted_lots = sorted(lots, key=lambda x: x.get('date', date.min), reverse=True)
        
        total_cost = Decimal('0')
        remaining = amount_to_sell
        remaining_lots = []
        
        for lot in sorted_lots:
            lot_amount = to_decimal(lot['amount'])
            lot_rate = to_decimal(lot['rate'])
            
            if remaining <= 0:
                remaining_lots.append(lot)
                continue
            
            if lot_amount <= remaining:
                total_cost += lot_amount * lot_rate
                remaining -= lot_amount
            else:
                total_cost += remaining * lot_rate
                remaining_lots.append({
                    **lot,
                    'amount': float(lot_amount - remaining)
                })
                remaining = Decimal('0')
        
        return round_currency(total_cost), remaining_lots
    
    @staticmethod
    def weighted_average_cost_basis(
        lots: List[Dict]
    ) -> Decimal:
        """
        Calculate weighted average cost basis from all lots.
        
        Args:
            lots: List of purchase lots
            
        Returns:
            Weighted average rate
        """
        total_amount = Decimal('0')
        total_cost = Decimal('0')
        
        for lot in lots:
            lot_amount = to_decimal(lot['amount'])
            lot_rate = to_decimal(lot['rate'])
            
            total_amount += lot_amount
            total_cost += lot_amount * lot_rate
        
        if total_amount <= 0:
            return Decimal('0')
        
        return round_rate(total_cost / total_amount)


def calculate_unrealized_pnl(
    positions: List[Dict],
    current_rates: Dict[str, Decimal],
    base_currency: str = 'USD'
) -> Dict:
    """
    Calculate unrealized P&L across multiple currency positions.
    
    Args:
        positions: List of positions with 'currency', 'amount', 'cost_basis_rate'
        current_rates: Dict of currency -> current rate
        base_currency: Base currency for reporting
        
    Returns:
        Dict with total and per-position unrealized P&L
    """
    total_cost = Decimal('0')
    total_current = Decimal('0')
    position_pnl = []
    
    for pos in positions:
        currency = pos['currency']
        amount = to_decimal(pos['amount'])
        cost_rate = to_decimal(pos.get('cost_basis_rate', 1))
        
        if currency == base_currency:
            current_rate = Decimal('1')
        else:
            current_rate = to_decimal(current_rates.get(currency, 1))
        
        cost_value = amount * cost_rate
        current_value = amount * current_rate
        unrealized = current_value - cost_value
        
        position_pnl.append({
            'currency': currency,
            'amount': float(amount),
            'cost_basis_rate': float(cost_rate),
            'current_rate': float(current_rate),
            'cost_value': float(round_currency(cost_value)),
            'current_value': float(round_currency(current_value)),
            'unrealized_pnl': float(round_currency(unrealized)),
            'pnl_pct': float((unrealized / cost_value * 100).quantize(PERCENTAGE_PRECISION)) if cost_value != 0 else 0
        })
        
        total_cost += cost_value
        total_current += current_value
    
    total_unrealized = total_current - total_cost
    
    return {
        'base_currency': base_currency,
        'total_cost_value': float(round_currency(total_cost)),
        'total_current_value': float(round_currency(total_current)),
        'total_unrealized_pnl': float(round_currency(total_unrealized)),
        'total_pnl_pct': float((total_unrealized / total_cost * 100).quantize(PERCENTAGE_PRECISION)) if total_cost != 0 else 0,
        'positions': position_pnl
    }


def convert_currency(
    amount: Decimal,
    from_currency: str,
    to_currency: str,
    rate: Decimal = None
) -> Decimal:
    """
    Convert amount between currencies.
    
    Args:
        amount: Amount to convert
        from_currency: Source currency
        to_currency: Target currency
        rate: FX rate (1 from = rate to), fetches if not provided
        
    Returns:
        Converted amount
    """
    amount = to_decimal(amount)
    
    if from_currency == to_currency:
        return amount
    
    if rate is None:
        from backend.services.fx_service import FXService
        rate = FXService.get_rate(from_currency, to_currency)
        
        if rate is None:
            raise ValueError(f"No rate for {from_currency}/{to_currency}")
    
    rate = to_decimal(rate)
    
    return round_currency(amount * rate)


def calculate_cross_rate(
    rate_a_to_base: Decimal,
    rate_b_to_base: Decimal
) -> Decimal:
    """
    Calculate cross rate between two currencies via base currency.
    
    If:
        1 A = rate_a_to_base BASE
        1 B = rate_b_to_base BASE
    Then:
        1 A = (rate_a_to_base / rate_b_to_base) B
    
    Args:
        rate_a_to_base: Rate of currency A to base
        rate_b_to_base: Rate of currency B to base
        
    Returns:
        Cross rate (1 A = X B)
    """
    rate_a = to_decimal(rate_a_to_base)
    rate_b = to_decimal(rate_b_to_base)
    
    if rate_b == 0:
        raise ValueError("Cannot calculate cross rate with zero denominator")
    
    return round_rate(rate_a / rate_b)


def calculate_pip_value(
    position_size: Decimal,
    currency_pair: str,
    base_currency: str = 'USD'
) -> Decimal:
    """
    Calculate the value of 1 pip for a currency position.
    
    A pip is typically 0.0001 for most pairs (0.01 for JPY pairs).
    
    Args:
        position_size: Size of position
        currency_pair: Currency pair (e.g., 'EUR/USD')
        base_currency: Account base currency
        
    Returns:
        Value of 1 pip in base currency
    """
    position_size = to_decimal(position_size)
    
    # Standard pip size (handle JPY pairs)
    quote_currency = currency_pair.split('/')[1] if '/' in currency_pair else currency_pair[-3:]
    pip_size = Decimal('0.01') if quote_currency == 'JPY' else Decimal('0.0001')
    
    # Pip value in quote currency
    pip_value_quote = position_size * pip_size
    
    # Convert to base currency if needed
    if quote_currency == base_currency:
        return round_currency(pip_value_quote, Decimal('0.0001'))
    
    return convert_currency(pip_value_quote, quote_currency, base_currency)


def format_currency(
    amount: Decimal,
    currency: str,
    include_symbol: bool = True
) -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount to format
        currency: Currency code
        include_symbol: Include currency symbol
        
    Returns:
        Formatted string
    """
    amount = round_currency(to_decimal(amount))
    
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CNY': '¥',
        'INR': '₹',
        'BRL': 'R$',
    }
    
    if include_symbol and currency in symbols:
        return f"{symbols[currency]}{amount:,.2f}"
    
    return f"{amount:,.2f} {currency}"


def validate_currency_code(code: str) -> bool:
    """Validate ISO 4217 currency code format."""
    if not code or len(code) != 3:
        return False
    
    return code.isalpha() and code.isupper()


def calculate_effective_rate(
    gross_amount: Decimal,
    net_amount: Decimal,
    fees: Decimal = None
) -> Decimal:
    """
    Calculate effective exchange rate including fees.
    
    Args:
        gross_amount: Amount before fees
        net_amount: Amount after fees (in different currency)
        fees: Known fee amount (optional for verification)
        
    Returns:
        Effective rate accounting for fees
    """
    gross = to_decimal(gross_amount)
    net = to_decimal(net_amount)
    
    if gross <= 0:
        return Decimal('0')
    
    return round_rate(net / gross)
