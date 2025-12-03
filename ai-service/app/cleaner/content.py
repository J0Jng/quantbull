"""
Content cleaner for processing and normalizing AI-generated content.
"""
import re
from html import unescape
from typing import Any, Dict, List, Optional

from app.cleaner.base import BaseCleaner
from app.utils.logger import logger


class ContentCleaner(BaseCleaner):
    """
    Cleaner for AI-generated content (articles, reports, scripts, etc.).
    """
    
    # HTML tag pattern
    HTML_PATTERN = re.compile(r"<[^>]+>")
    
    # Markdown code block pattern
    MARKDOWN_CODE_PATTERN = re.compile(r"```[\s\S]*?```")
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize content cleaner.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(name="content", config=config)
    
    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean AI-generated content.
        
        Args:
            data: Raw content data
            
        Returns:
            Cleaned content data
        """
        cleaned = data.copy()
        
        # Clean title if present
        if "title" in cleaned and cleaned["title"]:
            cleaned["title"] = self._clean_text(cleaned["title"])
        
        # Clean content
        if "content" in cleaned and cleaned["content"]:
            cleaned["content"] = self._clean_text(cleaned["content"])
        
        # Clean summary if present
        if "summary" in cleaned and cleaned["summary"]:
            cleaned["summary"] = self._clean_text(cleaned["summary"])
        
        # Remove markdown code blocks if needed
        if "remove_code_blocks" in self.config and self.config["remove_code_blocks"]:
            if "content" in cleaned:
                cleaned["content"] = self.MARKDOWN_CODE_PATTERN.sub("", cleaned["content"])
        
        # Ensure risk warning is present (for financial content)
        if "type" in cleaned and cleaned.get("type") in ["article", "daily_report"]:
            if "risk_warning" not in cleaned or not cleaned["risk_warning"]:
                cleaned["risk_warning"] = "以上内容不构成投资建议，股市有风险，投资需谨慎。"
        
        return cleaned
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize content format.
        
        Args:
            data: Cleaned data
            
        Returns:
            Normalized data
        """
        normalized = data.copy()
        
        # Ensure required fields have default values
        normalized.setdefault("status", "draft")
        normalized.setdefault("generated_by", "AI")
        
        # Normalize content length
        if "content" in normalized and normalized["content"]:
            max_length = self.config.get("max_content_length", 50000)
            if len(normalized["content"]) > max_length:
                normalized["content"] = normalized["content"][:max_length]
                self.logger.warning(f"Content truncated to {max_length} characters")
        
        return normalized
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate cleaned content.
        
        Args:
            data: Content data record
            
        Returns:
            True if valid, False otherwise
        """
        # Must have content
        if "content" not in data or not data["content"]:
            return False
        
        # Validate content length
        content = str(data["content"])
        min_length = self.config.get("min_content_length", 50)
        if len(content) < min_length:
            self.logger.warning(f"Content too short: {len(content)} characters")
            return False
        
        # Check for empty content (only whitespace)
        if not content.strip():
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
        text = self.HTML_PATTERN.sub("", text)
        
        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        # Remove special control characters
        text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f\x7f-\x9f]", "", text)
        
        return text
    
    def clean_markdown(self, markdown: str) -> str:
        """
        Clean and normalize markdown content.
        
        Args:
            markdown: Markdown text
            
        Returns:
            Cleaned markdown text
        """
        cleaned = markdown
        
        # Remove excessive blank lines
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        
        # Ensure proper line breaks
        cleaned = cleaned.replace("\r\n", "\n").replace("\r", "\n")
        
        return cleaned.strip()
    
    def extract_code_blocks(self, content: str) -> List[str]:
        """
        Extract code blocks from content.
        
        Args:
            content: Content with potential code blocks
            
        Returns:
            List of extracted code blocks
        """
        matches = self.MARKDOWN_CODE_PATTERN.findall(content)
        # Remove ``` markers
        code_blocks = []
        for match in matches:
            code = match.strip()
            # Remove opening and closing ```
            if code.startswith("```"):
                code = code[3:]
            if code.endswith("```"):
                code = code[:-3]
            code_blocks.append(code.strip())
        
        return code_blocks

