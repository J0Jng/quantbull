"""
Base crawler class for user data collection and synchronization.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from app.utils.logger import logger


class BaseCrawler(ABC):
    """
    Abstract base class for all user data crawlers.
    
    All crawlers should inherit from this class and implement
    the required methods for syncing user data from external sources.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize crawler.
        
        Args:
            name: Crawler name
            config: Optional configuration dictionary
        """
        self.name = name
        self.config = config or {}
        self.logger = logger.getChild(f"crawler.{name}")
    
    @abstractmethod
    async def fetch(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Fetch user data from the external source.
        
        Args:
            **kwargs: Additional parameters for fetching
            
        Returns:
            List of fetched user data records
            
        Raises:
            Exception: If fetching fails
        """
        pass
    
    @abstractmethod
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate fetched user data record.
        
        Args:
            data: User data record to validate
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    def preprocess(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess data before validation.
        Override this method to add custom preprocessing.
        
        Args:
            data: Raw user data record
            
        Returns:
            Preprocessed data record
        """
        return data
    
    def postprocess(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Postprocess data after validation.
        Override this method to add custom postprocessing.
        
        Args:
            data: Validated user data record
            
        Returns:
            Postprocessed data record
        """
        return data
    
    async def crawl(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Main crawl method that orchestrates the crawling process.
        
        Args:
            **kwargs: Additional parameters for crawling
            
        Returns:
            List of processed user data records
        """
        try:
            self.logger.info(f"Starting crawl: {self.name}")
            
            # Fetch data
            raw_data = await self.fetch(**kwargs)
            self.logger.info(f"Fetched {len(raw_data)} user records")
            
            # Process data
            processed_data = []
            for record in raw_data:
                # Preprocess
                record = self.preprocess(record)
                
                # Validate
                if not self.validate(record):
                    self.logger.warning(f"Invalid user record skipped: {record.get('id', 'unknown')}")
                    continue
                
                # Postprocess
                record = self.postprocess(record)
                processed_data.append(record)
            
            self.logger.info(f"Processed {len(processed_data)} valid user records")
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Crawl failed: {e}", exc_info=True)
            raise

