"""
Market data cleaner for processing and validating market data.
"""
from datetime import datetime
from typing import Any, Dict, Optional

from app.cleaner.base import BaseCleaner
from app.utils.logger import logger


class MarketDataCleaner(BaseCleaner):
    """
    Cleaner for market data validation and normalization.
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
            cleaned["code"] = str(cleaned["code"]).upper().strip()
        
        # Ensure numeric fields are floats
        numeric_fields = ["open", "high", "low", "close", "volume", "amount"]
        for field in numeric_fields:
            if field in cleaned:
                try:
                    value = cleaned[field]
                    if value is not None:
                        cleaned[field] = float(value)
                    else:
                        cleaned[field] = None
                except (ValueError, TypeError):
                    cleaned[field] = None
        
        # Validate price consistency
        if all(k in cleaned and cleaned[k] for k in ["open", "high", "low", "close"]):
            # Ensure high >= max(open, close) and low <= min(open, close)
            max_price = max(cleaned["open"], cleaned["close"])
            min_price = min(cleaned["open"], cleaned["close"])
            
            if cleaned["high"] < max_price:
                cleaned["high"] = max_price
                self.logger.warning(f"Adjusted high price for {cleaned.get('code')}")
            
            if cleaned["low"] > min_price:
                cleaned["low"] = min_price
                self.logger.warning(f"Adjusted low price for {cleaned.get('code')}")
        
        # Normalize date format
        if "date" in cleaned:
            cleaned["date"] = self._normalize_date(cleaned["date"])
        
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
        
        # Calculate change and change_pct if not present
        if "change_pct" not in normalized and "close" in normalized and "open" in normalized:
            if normalized.get("open") and normalized.get("close"):
                change = normalized["close"] - normalized["open"]
                normalized["change"] = change
                normalized["change_pct"] = (change / normalized["open"]) * 100
        
        # Ensure timestamp exists
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
        required = ["code", "date", "close"]
        if not all(field in data for field in required):
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
        
        # Validate volume is non-negative
        if "volume" in data and data["volume"]:
            if data["volume"] < 0:
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

