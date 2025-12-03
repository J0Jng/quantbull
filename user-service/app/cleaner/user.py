"""
User data cleaner for processing and validating user information.
"""
import re
from typing import Any, Dict, Optional

from app.cleaner.base import BaseCleaner
from app.config import settings
from app.utils.logger import logger


class UserDataCleaner(BaseCleaner):
    """
    Cleaner for user data validation and normalization.
    """
    
    # Email validation pattern
    EMAIL_PATTERN = re.compile(
        r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    )
    
    # Phone validation pattern (Chinese mobile)
    PHONE_PATTERN = re.compile(r"^1[3-9]\d{9}$")
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize user data cleaner.
        
        Args:
            config: Configuration dictionary
        """
        super().__init__(name="user", config=config)
    
    def clean(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean user data record.
        
        Args:
            data: Raw user data
            
        Returns:
            Cleaned user data
        """
        cleaned = data.copy()
        
        # Clean email
        if "email" in cleaned and cleaned["email"]:
            cleaned["email"] = self._clean_email(cleaned["email"])
        
        # Clean phone
        if "phone" in cleaned and cleaned["phone"]:
            cleaned["phone"] = self._clean_phone(cleaned["phone"])
        
        # Clean username
        if "username" in cleaned and cleaned["username"]:
            cleaned["username"] = self._clean_username(cleaned["username"])
        
        # Clean nickname
        if "nickname" in cleaned and cleaned["nickname"]:
            cleaned["nickname"] = self._clean_nickname(cleaned["nickname"])
        
        # Remove sensitive fields that shouldn't be stored
        sensitive_fields = ["password", "password_hash", "token"]
        for field in sensitive_fields:
            cleaned.pop(field, None)
        
        return cleaned
    
    def normalize(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize user data format.
        
        Args:
            data: Cleaned data
            
        Returns:
            Normalized data
        """
        normalized = data.copy()
        
        # Ensure lowercase for email and username
        if "email" in normalized and normalized["email"]:
            normalized["email"] = normalized["email"].lower()
        
        if "username" in normalized and normalized["username"]:
            normalized["username"] = normalized["username"].lower()
        
        # Set default role if not present
        normalized.setdefault("role", "user")
        
        # Set default status if not present
        normalized.setdefault("status", "active")
        
        return normalized
    
    def validate(self, data: Dict[str, Any]) -> bool:
        """
        Validate user data.
        
        Args:
            data: User data record
            
        Returns:
            True if valid, False otherwise
        """
        # Must have at least email or username
        if "email" not in data and "username" not in data:
            self.logger.warning("User data missing email or username")
            return False
        
        # Validate email format if present
        if "email" in data and data["email"]:
            if not self.EMAIL_PATTERN.match(data["email"]):
                self.logger.warning(f"Invalid email format: {data['email']}")
                return False
        
        # Validate phone format if present
        if "phone" in data and data["phone"]:
            if not self.PHONE_PATTERN.match(data["phone"]):
                self.logger.warning(f"Invalid phone format: {data['phone']}")
                return False
        
        # Validate role
        valid_roles = ["user", "admin", "vip", "premium"]
        if "role" in data and data["role"] not in valid_roles:
            self.logger.warning(f"Invalid role: {data['role']}")
            return False
        
        return True
    
    def _clean_email(self, email: Any) -> str:
        """
        Clean and normalize email address.
        
        Args:
            email: Email address
            
        Returns:
            Cleaned email address
        """
        email = str(email).strip().lower()
        return email
    
    def _clean_phone(self, phone: Any) -> str:
        """
        Clean and normalize phone number.
        
        Args:
            phone: Phone number
            
        Returns:
            Cleaned phone number (digits only)
        """
        phone = re.sub(r"[^\d]", "", str(phone))
        return phone
    
    def _clean_username(self, username: Any) -> str:
        """
        Clean and normalize username.
        
        Args:
            username: Username
            
        Returns:
            Cleaned username
        """
        username = str(username).strip()
        # Remove special characters, keep only alphanumeric, underscore, dash
        username = re.sub(r"[^\w-]", "", username)
        return username
    
    def _clean_nickname(self, nickname: Any) -> str:
        """
        Clean and normalize nickname.
        
        Args:
            nickname: User nickname
            
        Returns:
            Cleaned nickname
        """
        nickname = str(nickname).strip()
        # Remove excessive whitespace
        nickname = re.sub(r"\s+", " ", nickname)
        # Limit length
        max_length = 50
        if len(nickname) > max_length:
            nickname = nickname[:max_length]
        return nickname
    
    def validate_password(self, password: str) -> tuple[bool, Optional[str]]:
        """
        Validate password against security requirements.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if len(password) < settings.password_min_length:
            return False, f"Password must be at least {settings.password_min_length} characters"
        
        if settings.password_require_uppercase and not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        
        if settings.password_require_lowercase and not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        
        if settings.password_require_numbers and not re.search(r"\d", password):
            return False, "Password must contain at least one number"
        
        if settings.password_require_special and not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"
        
        return True, None

