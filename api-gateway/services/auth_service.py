from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from core.config import settings
from schemas.auth import TokenData


class AuthService:
    """认证服务"""
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """创建访问令牌"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret,
            algorithm=settings.jwt_algorithm
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """验证令牌"""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret,
                algorithms=[settings.jwt_algorithm]
            )
            username = payload.get("sub")
            user_id = payload.get("user_id")
            if not isinstance(username, str):
                return None
            if user_id is None:
                return None
            try:
                user_id_int = int(user_id)
            except (TypeError, ValueError):
                return None
            return TokenData(username=username, user_id=user_id_int)
        except JWTError:
            return None
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> bool:
        """验证用户（示例实现，实际应连接 user-service:用户认证、权限管理)"""
        # TODO: 实际应调用 user-service 进行验证
        # 这里仅作为示例
        return username == "admin" and password == "admin123"
