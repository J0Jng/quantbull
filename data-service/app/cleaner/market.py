"""
Market data cleaner for processing stock quotes and K-line data.
"""
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from app.cleaner.base import BaseCleaner
from app.utils.logger import logger


class MarketDataCleaner(BaseCleaner):
    """
    Cleaner for market data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize market data cleaner.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(name="market", config=config)
    
    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean market data record.
        
        Args:
            data: Raw market data
            
        Returns:
            Cleaned market data
        """
        cleaned = data.copy()
        
        # Normalize stock code
        if "code" in cleaned:
            cleaned["code"] = cleaned["code"].upper().strip()
        
        # Convert numeric fields
        numeric_fields = ["open", "high", "low", "close", "volume", "amount"]
        for field in numeric_fields:
            if field in cleaned:
                try:
                    cleaned[field] = float(cleaned[field]) if cleaned[field] else None
                except (ValueError, TypeError):
                    cleaned[field] = None
        
        # Normalize date format
        if "date" in cleaned:
            cleaned["date"] = self._normalize_date(cleaned["date"])
        
        # Calculate change percentage if not present
        if "change_pct" not in cleaned and "close" in cleaned and "open" in cleaned:
            if cleaned.get("open") and cleaned.get("close"):
                cleaned["change_pct"] = (
                    (cleaned["close"] - cleaned["open"]) / cleaned["open"] * 100
                )
        
        return cleaned
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize market data format.
        
        Args:
            data: Cleaned data
            
        Returns:
            Normalized data
        """
        normalized = data.copy()
        
        # Ensure required fields
        if "timestamp" not in normalized and "date" in normalized:
            try:
                date_obj = datetime.strptime(normalized["date"], "%Y-%m-%d")
                normalized["timestamp"] = int(date_obj.timestamp())
            except (ValueError, TypeError):
                pass
        
        return normalized
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate market data.
        
        Args:
            data: Market data record
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if "code" not in data or "date" not in data:
            return False
        
        # Validate price range (0.01 - 10000)
        if "close" in data and data["close"]:
            if not (0.01 <= data["close"] <= 10000):
                self.logger.warning(f"Invalid price: {data['close']}")
                return False
        
        # Validate high >= low
        if "high" in data and "low" in data:
            if data["high"] and data["low"]:
                if data["high"] < data["low"]:
                    return False
        
        return True
    
    def _normalize_date(self, date_str: Any) -> str:
        """
        Normalize date string to YYYY-MM-DD format.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Normalized date string
        """
        if isinstance(date_str, datetime):
            return date_str.strftime("%Y-%m-%d")
        
        date_str = str(date_str).strip()
        
        # Try different formats
        formats = ["%Y%m%d", "%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y"]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return date_str

