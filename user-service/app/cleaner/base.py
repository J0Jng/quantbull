"""
Base cleaner class for user data processing.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.utils.logger import logger


class BaseCleaner(ABC):
    """
    Abstract base class for all user data cleaners.
    
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
        Clean a single user data record.
        
        Args:
            data: Raw user data record
            
        Returns:
            Cleaned user data record
            
        Raises:
            ValueError: If data cannot be cleaned
        """
        pass
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize user data format.
        Override this method to add custom normalization.
        
        Args:
            data: User data record
            
        Returns:
            Normalized user data record
        """
        return data
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate cleaned user data.
        
        Args:
            data: Cleaned user data record
            
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def clean_batch(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean a batch of user data records.
        
        Args:
            data_list: List of raw user data records
            
        Returns:
            List of cleaned user data records
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
                    self.logger.warning(f"Validation failed for user record {idx}")
                    
            except Exception as e:
                self.logger.error(f"Error cleaning user record {idx}: {e}")
                continue
        
        self.logger.info(
            f"Cleaned {len(cleaned_data)}/{len(data_list)} user records"
        )
        return cleaned_data

