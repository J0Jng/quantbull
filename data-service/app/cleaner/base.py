"""
Base cleaner class for data processing.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.utils.logger import logger


class BaseCleaner(ABC):
    """
    Abstract base class for all data cleaners.
    
    All cleaners should inherit from this class and implement
    the required methods.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize cleaner.
        
        Args:
            name: Cleaner name
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.logger = logger.getChild(f"cleaner.{name}")
    
    @abstractmethod
    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean a single data record.
        
        Args:
            data: Raw data record
            
        Returns:
            Cleaned data record
            
        Raises:
            ValueError: If data cannot be cleaned
        """
        pass
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize data format.
        Override this method to add custom normalization.
        
        Args:
            data: Data record
            
        Returns:
            Normalized data record
        """
        return data
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate cleaned data.
        
        Args:
            data: Cleaned data record
            
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def clean_batch(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean a batch of data records.
        
        Args:
            data_list: List of raw data records
            
        Returns:
            List of cleaned data records
        """
        cleaned_data = []
        
        for idx, record in enumerate(data_list):
            try:
                # Clean
                cleaned = self.clean(record)
                
                # Normalize
                normalized = self.normalize(cleaned)
                
                # Validate
                if self.validate(normalized):
                    cleaned_data.append(normalized)
                else:
                    self.logger.warning(f"Validation failed for record {idx}")
                    
            except Exception as e:
                self.logger.error(f"Error cleaning record {idx}: {e}")
                continue
        
        self.logger.info(
            f"Cleaned {len(cleaned_data)}/{len(data_list)} records"
        )
        return cleaned_data

