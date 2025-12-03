"""
Base cleaner class for AI-generated content processing.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.utils.logger import logger


class BaseCleaner(ABC):
    """
    Abstract base class for all content cleaners in AI service.
    
    All cleaners should inherit from this class and implement
    the required methods for cleaning AI-generated content.
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
        Clean a single content record.
        
        Args:
            data: Raw content record
            
        Returns:
            Cleaned content record
            
        Raises:
            ValueError: If data cannot be cleaned
        """
        pass
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize content format.
        Override this method to add custom normalization.
        
        Args:
            data: Content record
            
        Returns:
            Normalized content record
        """
        return data
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate cleaned content.
        
        Args:
            data: Cleaned content record
            
        Returns:
            True if valid, False otherwise
        """
        return True
    
    def clean_batch(self, data_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Clean a batch of content records.
        
        Args:
            data_list: List of raw content records
            
        Returns:
            List of cleaned content records
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
                    self.logger.warning(f"Validation failed for content record {idx}")
                    
            except Exception as e:
                self.logger.error(f"Error cleaning content record {idx}: {e}")
                continue
        
        self.logger.info(
            f"Cleaned {len(cleaned_data)}/{len(data_list)} content records"
        )
        return cleaned_data

