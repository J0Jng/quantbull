"""
External user data crawler for syncing users from other systems.
"""
from typing import Any, Dict, List, Optional

from app.crawler.base import BaseCrawler
from app.utils.logger import logger


class ExternalUserCrawler(BaseCrawler):
    """
    Generic crawler for syncing user data from external systems.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize external user crawler.
        
        Args:
            config: Configuration dictionary with API credentials
        """
        super().__init__(name="external", config=config)
        self.api_endpoint = config.get("api_endpoint", "") if config else ""
        self.api_key = config.get("api_key", "") if config else ""
    
    async def fetch(
        self,
        source: Optional[str] = None,
        limit: Optional[int] = None,
        **kwargs: Any,
    ) -> List[Dict[str, Any]]:
        """
        Fetch user data from external system.
        
        Args:
            source: External system identifier
            limit: Maximum number of users to fetch
            **kwargs: Additional parameters
            
        Returns:
            List of user data records
        """
        # TODO: Implement actual external API integration
        self.logger.info(f"Fetching user data from external source: {source}")
        
        records = []
        # Example implementation:
        # 1. Authenticate with external API
        # 2. Fetch user list
        # 3. Transform to internal format
        
        return records
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate external user data record.
        
        Args:
            data: User data record
            
        Returns:
            True if valid, False otherwise
        """
        # Basic validation
        if "id" not in data and "email" not in data and "username" not in data:
            return False
        
        # Validate email format if present
        if "email" in data and data["email"]:
            email = str(data["email"])
            if "@" not in email or "." not in email.split("@")[1]:
                return False
        
        return True
    
    def preprocess(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Preprocess external user data.
        
        Args:
            data: Raw external user data
            
        Returns:
            Preprocessed data
        """
        processed = data.copy()
        
        # Normalize email to lowercase
        if "email" in processed and processed["email"]:
            processed["email"] = str(processed["email"]).lower().strip()
        
        # Normalize username
        if "username" in processed and processed["username"]:
            processed["username"] = str(processed["username"]).strip()
        
        return processed

