"""
Extraction Agent - Transforms heterogeneous alternative data into normalized financial records
"""
from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import Transaction
import json


class ExtractionAgent:
    """Extracts and normalizes financial data from various sources"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def execute(self, sme_id: int, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute extraction agent
        inputs: {
            "data_sources": [
                {"type": "bank_csv", "data": "csv_content"},
                {"type": "ecommerce", "data": "csv_content"},
                {"type": "ocr", "data": {...}}
            ]
        }
        """
        data_sources = inputs.get("data_sources", [])
        extracted_transactions = []
        
        for source in data_sources:
            source_type = source.get("type")
            source_data = source.get("data")
            
            if source_type == "bank_csv":
                transactions = self._extract_from_bank_csv(sme_id, source_data)
                extracted_transactions.extend(transactions)
            
            elif source_type == "ecommerce":
                transactions = self._extract_from_ecommerce(sme_id, source_data)
                extracted_transactions.extend(transactions)
            
            elif source_type == "ocr":
                transactions = self._extract_from_ocr(sme_id, source_data)
                extracted_transactions.extend(transactions)
        
        # Store transactions in database
        for tx_data in extracted_transactions:
            transaction = Transaction(**tx_data)
            self.db.add(transaction)
        
        self.db.commit()
        
        return {
            "status": "success",
            "transactions_extracted": len(extracted_transactions),
            "sme_id": sme_id
        }
    
    def _extract_from_bank_csv(self, sme_id: int, csv_content: str) -> List[Dict[str, Any]]:
        """Extract transactions from bank CSV"""
        try:
            df = pd.read_csv(pd.StringIO(csv_content))
            
            # Normalize column names (handle variations)
            column_mapping = {
                "date": ["date", "transaction_date", "Date", "Transaction Date"],
                "amount": ["amount", "Amount", "value", "Value"],
                "description": ["description", "Description", "memo", "Memo", "details", "Details"],
                "type": ["type", "Type", "transaction_type", "Transaction Type"]
            }
            
            normalized_df = self._normalize_columns(df, column_mapping)
            
            transactions = []
            for _, row in normalized_df.iterrows():
                # Determine transaction type
                amount = float(row.get("amount", 0))
                tx_type = row.get("type", "").lower() if pd.notna(row.get("type")) else ""
                
                if "debit" in tx_type or amount < 0:
                    transaction_type = "expense"
                    amount = abs(amount)
                else:
                    transaction_type = "income"
                
                # Categorize transaction
                category = self._categorize_transaction(row.get("description", ""))
                
                transactions.append({
                    "sme_id": sme_id,
                    "transaction_date": pd.to_datetime(row.get("date")).to_pydatetime(),
                    "amount": amount,
                    "transaction_type": transaction_type,
                    "category": category,
                    "description": str(row.get("description", "")),
                    "source": "bank_csv",
                    "raw_data": row.to_dict()
                })
            
            return transactions
        
        except Exception as e:
            raise Exception(f"Failed to extract from bank CSV: {str(e)}")
    
    def _extract_from_ecommerce(self, sme_id: int, csv_content: str) -> List[Dict[str, Any]]:
        """Extract transactions from e-commerce sales CSV"""
        try:
            df = pd.read_csv(pd.StringIO(csv_content))
            
            column_mapping = {
                "date": ["date", "order_date", "sale_date", "Date"],
                "amount": ["amount", "total", "revenue", "sales", "Amount"],
                "description": ["description", "product", "order_id", "Description"]
            }
            
            normalized_df = self._normalize_columns(df, column_mapping)
            
            transactions = []
            for _, row in normalized_df.iterrows():
                amount = float(row.get("amount", 0))
                
                transactions.append({
                    "sme_id": sme_id,
                    "transaction_date": pd.to_datetime(row.get("date")).to_pydatetime(),
                    "amount": amount,
                    "transaction_type": "income",
                    "category": "sales",
                    "description": f"E-commerce sale: {row.get('description', '')}",
                    "source": "ecommerce",
                    "raw_data": row.to_dict()
                })
            
            return transactions
        
        except Exception as e:
            raise Exception(f"Failed to extract from e-commerce CSV: {str(e)}")
    
    def _extract_from_ocr(self, sme_id: int, ocr_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract transactions from OCR-extracted invoice/receipt data"""
        transactions = []
        
        try:
            # OCR data structure: {"date": "...", "amount": "...", "items": [...]}
            amount = float(ocr_data.get("amount", 0))
            date_str = ocr_data.get("date", datetime.utcnow().isoformat())
            
            transaction_type = "expense"  # Invoices/receipts are typically expenses
            
            transactions.append({
                "sme_id": sme_id,
                "transaction_date": pd.to_datetime(date_str).to_pydatetime(),
                "amount": amount,
                "transaction_type": transaction_type,
                "category": "purchase",
                "description": f"OCR: {ocr_data.get('description', 'Invoice/Receipt')}",
                "source": "ocr",
                "raw_data": ocr_data
            })
        
        except Exception as e:
            raise Exception(f"Failed to extract from OCR data: {str(e)}")
        
        return transactions
    
    def _normalize_columns(self, df: pd.DataFrame, mapping: Dict[str, List[str]]) -> pd.DataFrame:
        """Normalize column names based on mapping"""
        normalized = {}
        for standard_name, possible_names in mapping.items():
            for col in df.columns:
                if col in possible_names:
                    normalized[col] = standard_name
                    break
        
        return df.rename(columns=normalized)
    
    def _categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description"""
        description_lower = description.lower()
        
        categories = {
            "salary": ["salary", "payroll", "wage"],
            "rent": ["rent", "lease"],
            "utilities": ["electricity", "water", "internet", "phone", "utility"],
            "supplies": ["supplies", "materials", "inventory"],
            "marketing": ["marketing", "advertising", "ad"],
            "travel": ["travel", "transport", "fuel", "gas"],
            "sales": ["sale", "revenue", "income", "payment received"]
        }
        
        for category, keywords in categories.items():
            if any(keyword in description_lower for keyword in keywords):
                return category
        
        return "other"
