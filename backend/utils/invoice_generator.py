import os
import json
from datetime import datetime

class InvoiceGenerator:
    """
    Utility to generate digital invoices and packing slips for bulk procurement.
    """
    
    @staticmethod
    def generate_invoice_data(order):
        """Prepares a structured dictionary for PDF/HTML rendering"""
        from backend.models.procurement import ProcurementItem
        item = ProcurementItem.query.get(order.item_id)
        
        return {
            'invoice_number': f"INV-{order.id:06d}",
            'date': order.created_at.strftime("%Y-%m-%d"),
            'buyer_id': order.buyer_id,
            'vendor_name': order.vendor.company_name,
            'items': [
                {
                    'name': item.name,
                    'qty': order.quantity,
                    'unit_price': order.unit_price,
                    'total': order.quantity * order.unit_price
                }
            ],
            'tax': order.tax_amount,
            'shipping': order.shipping_cost,
            'grand_total': order.total_amount,
            'address': order.delivery_address
        }

    @staticmethod
    def save_as_log(order):
        """Serializes invoice to a JSON log for audit (Mocking PDF generation)"""
        invoice = InvoiceGenerator.generate_invoice_data(order)
        # In real app, this would use a PDF library
        return json.dumps(invoice, indent=2)
