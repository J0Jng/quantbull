"""
Factor data cleaner for processing and validating factor data.
"""
from typing import Any, Dict, Optional

import numpy as np

from app.cleaner.base import BaseCleaner
from app.utils.logger import logger


class FactorDataCleaner(BaseCleaner):
    """
    Cleaner for factor data validation and normalization.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize factor data cleaner.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(name="factor", config=config)
    
    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean factor data record.
        
        Args:
            data: Raw factor data
            
        Returns:
            Cleaned factor data
        """
        cleaned = data.copy()
        
        # Normalize stock code
        if "code" in cleaned:
            cleaned["code"] = str(cleaned["code"]).upper().strip()
        
        # Normalize factor name
        if "factor_name" in cleaned:
            cleaned["factor_name"] = str(cleaned["factor_name"]).lower().strip()
        
        # Ensure factor_value is numeric
        if "factor_value" in cleaned:
            try:
                value = cleaned["factor_value"]
                if value is not None:
                    cleaned["factor_value"] = float(value)
                else:
                    cleaned["factor_value"] = None
            except (ValueError, TypeError):
                cleaned["factor_value"] = None
        
        # Handle NaN and infinity
        if "factor_value" in cleaned and cleaned["factor_value"] is not None:
            if np.isnan(cleaned["factor_value"]) or np.isinf(cleaned["factor_value"]):
                cleaned["factor_value"] = None
        
        return cleaned
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize factor data format.
        
        Args:
            data: Cleaned data
            
        Returns:
            Normalized data
        """
        normalized = data.copy()
        
        # Normalize date if present
        if "date" in normalized:
            normalized["date"] = self._normalize_date(normalized["date"])
        
        return normalized
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate factor data.
        
        Args:
            data: Factor data record
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required = ["code", "factor_name", "factor_value"]
        if not all(field in data for field in required):
            return False
        
        # Validate factor_value is not None
        if data["factor_value"] is None:
            return False
        
        # Validate factor_value is finite
        try:
            value = float(data["factor_value"])
            if np.isnan(value) or np.isinf(value):
                return False
        except (ValueError, TypeError):
            return False
        
        return True
    
    def _normalize_date(self, date_str: Any) -> str:
        """
        Normalize date string to YYYY-MM-DD format.
        
        Args:
            date_str: Date string
            
        Returns:
            Normalized date string
        """
        from datetime import datetime
        
        if isinstance(date_str, datetime):
            return date_str.strftime("%Y-%m-%d")
        
        date_str = str(date_str).strip()
        formats = ["%Y%m%d", "%Y-%m-%d", "%Y/%m/%d"]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return date_str

