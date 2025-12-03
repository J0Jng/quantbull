"""
News data cleaner for processing financial news.
"""
import re
from html import unescape
from typing import Any, Dict, List, Optional

from app.cleaner.base import BaseCleaner
from app.utils.logger import logger


class NewsCleaner(BaseCleaner):
    """
    Cleaner for news data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize news cleaner.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(name="news", config=config)
        # HTML tag pattern
        self.html_pattern = re.compile(r"<[^>]+>")
    
    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean news record.
        
        Args:
            data: Raw news data
            
        Returns:
            Cleaned news data
        """
        cleaned = data.copy()
        
        # Clean title
        if "title" in cleaned:
            cleaned["title"] = self._clean_text(cleaned["title"])
        
        # Clean content
        if "content" in cleaned:
            cleaned["content"] = self._clean_text(cleaned["content"])
        
        # Extract summary from content if not present
        if "summary" not in cleaned and "content" in cleaned:
            cleaned["summary"] = cleaned["content"][:200] + "..."
        
        # Normalize publish time
        if "publish_time" in cleaned:
            cleaned["publish_time"] = self._normalize_datetime(
                cleaned["publish_time"]
            )
        
        # Extract stock codes from content
        if "related_stocks" not in cleaned:
            cleaned["related_stocks"] = self._extract_stock_codes(
                cleaned.get("content", "") + " " + cleaned.get("title", "")
            )
        
        return cleaned
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize news data format.
        
        Args:
            data: Cleaned data
            
        Returns:
            Normalized data
        """
        normalized = data.copy()
        
        # Ensure required fields have default values
        normalized.setdefault("author", "Unknown")
        normalized.setdefault("category", "finance")
        normalized.setdefault("tags", [])
        
        return normalized
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate news data.
        
        Args:
            data: News data record
            
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        required = ["title", "content", "publish_time"]
        if not all(field in data for field in required):
            return False
        
        # Validate content length
        if len(data.get("content", "")) < 50:
            return False
        
        return True
    
    def _clean_text(self, text: str) -> str:
        """
        Clean HTML and normalize text.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Unescape HTML entities
        text = unescape(text)
        
        # Remove HTML tags
        text = self.html_pattern.sub("", text)
        
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text).strip()
        
        return text
    
    def _normalize_datetime(self, dt_str: Any) -> str:
        """
        Normalize datetime string to ISO format.
        
        Args:
            dt_str: Datetime string
            
        Returns:
            Normalized datetime string (ISO format)
        """
        # TODO: Implement datetime normalization
        return str(dt_str)
    
    def _extract_stock_codes(self, text: str) -> List[str]:
        """
        Extract stock codes from text.
        
        Args:
            text: Text to search
            
        Returns:
            List of stock codes found
        """
        # Pattern: 6-digit code (000001, 600000, etc.)
        pattern = r"\b(?:00|30|60|68|43|83|87)[0-9]{4}\b"
        codes = re.findall(pattern, text)
        return list(set(codes))  # Remove duplicates

