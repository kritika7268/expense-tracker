import csv
import io
from typing import List
from app.models.transaction import Transaction

def generate_transactions_csv(transactions: List[Transaction]) -> str:
    """
    Generates RFC-4180 compliant CSV string for given transactions.
    Columns: Date, Title, Type, Category, Amount, Payment Method, Description
    """
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
    
    # Header
    writer.writerow([
        "Date",
        "Title",
        "Type",
        "Category",
        "Amount",
        "Payment Method",
        "Description"
    ])
    
    # Rows
    for t in transactions:
        cat_name = t.category.name if t.category else "Uncategorized"
        writer.writerow([
            t.transaction_date.strftime("%Y-%m-%d"),
            t.title,
            t.type.capitalize(),
            cat_name,
            f"{float(t.amount):.2f}",
            t.payment_method,
            t.description or ""
        ])
        
    return output.getvalue()
