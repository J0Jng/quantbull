from datetime import datetime, timezone
import hashlib
import json
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, Field, field_validator
from sqlmodel import Session

from auth.jwt import verify_token
from core.config import settings
from models import User, get_session, get_user_by_username

router = APIRouter(prefix="/api/investor", tags=["investor"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Envelope(BaseModel):
    code: int
    message: str
    data: dict | list | None


class CertificationRequest(BaseModel):
    real_name: Optional[str] = Field(default=None)
    id_card: Optional[str] = Field(default=None)
    risk_level: str
    asset_type: str
    risk_confirmed: bool

    @field_validator("real_name", "id_card", mode="before")
    @classmethod
    def normalize_empty(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            trimmed = value.strip()
            return trimmed or None
        return value


class InvestorStatusResponse(BaseModel):
    qualified_investor: bool
    certified_at: Optional[str]
    risk_level: Optional[str]
    asset_type: Optional[str]
    tags: List[str]
    real_name_masked: Optional[str] = None
    id_card_masked: Optional[str] = None
    id_card_last4: Optional[str] = None


RISK_LEVEL_MAP = {
    "conservative": "风险偏好：保守型",
    "moderate": "风险偏好：稳健型",
    "aggressive": "风险偏好：进取型",
}

ASSET_TYPE_MAP = {
    "financial": "合格条件：金融资产≥300万",
    "income": "合格条件：年均收入≥50万",
    "experience": "合格条件：投资经验≥2年",
}


def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)) -> User:
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid token")

    user = get_user_by_username(session, payload["username"])
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="user not found")

    return user


def _hash_id_card(id_card: str) -> str:
    salt = getattr(settings, "investor_id_salt", "investor-salt")
    value = f"{id_card}{salt}"
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _mask_id_card(id_card: str) -> tuple[str, str]:
    last4 = id_card[-4:] if len(id_card) >= 4 else id_card
    masked = f"{'*' * max(len(id_card) - 4, 0)}{last4}"
    return masked, last4


def _mask_real_name(real_name: str) -> str:
    if not real_name:
        return ""
    if len(real_name) == 1:
        return "*"
    return f"{real_name[0]}{'*' * (len(real_name) - 1)}"


def _build_tags(risk_level: str, asset_type: str, risk_confirmed: bool) -> List[str]:
    tags = ["合格投资者（已认证）"]
    risk_tag = RISK_LEVEL_MAP.get(risk_level)
    if risk_tag:
        tags.append(risk_tag)
    asset_tag = ASSET_TYPE_MAP.get(asset_type)
    if asset_tag:
        tags.append(asset_tag)
    if risk_confirmed:
        tags.append("已确认风险提示")
    return tags


def _status_payload(user: User) -> InvestorStatusResponse:
    tags = []
    if user.investor_tags:
        try:
            tags = json.loads(user.investor_tags)
        except Exception:
            tags = []
    masked_name = _mask_real_name(user.investor_real_name or "") if user.investor_real_name else None
    masked_id = None
    if user.investor_id_card_last4:
        masked_id = f"{'*' * 14}{user.investor_id_card_last4}" if len(user.investor_id_card_last4) == 4 else user.investor_id_card_last4
    return InvestorStatusResponse(
        qualified_investor=bool(user.qualified_investor),
        certified_at=user.investor_certified_at.isoformat() if user.investor_certified_at else None,
        risk_level=user.investor_risk_level,
        asset_type=user.investor_asset_type,
        tags=tags,
        real_name_masked=masked_name,
        id_card_masked=masked_id,
        id_card_last4=user.investor_id_card_last4,
    )


@router.post("/certification")
async def submit_certification(
    payload: CertificationRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Envelope:
    if not payload.risk_confirmed:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="risk confirmation required")

    if payload.risk_level not in RISK_LEVEL_MAP:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid risk_level")

    if payload.asset_type not in ASSET_TYPE_MAP:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="invalid asset_type")

    id_card_hash = None
    id_card_masked = None
    id_card_last4 = None
    if payload.id_card:
        id_card_hash = _hash_id_card(payload.id_card)
        id_card_masked, id_card_last4 = _mask_id_card(payload.id_card)
    tags = _build_tags(payload.risk_level, payload.asset_type, payload.risk_confirmed)

    current_user.qualified_investor = True
    current_user.investor_certified_at = datetime.now(timezone.utc)
    current_user.investor_risk_level = payload.risk_level
    current_user.investor_asset_type = payload.asset_type
    current_user.investor_tags = json.dumps(tags, ensure_ascii=False)
    current_user.investor_real_name = payload.real_name
    current_user.investor_id_card_hash = id_card_hash
    current_user.investor_id_card_last4 = id_card_last4

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    data = _status_payload(current_user).model_dump()
    if id_card_masked:
        data["id_card_masked"] = id_card_masked

    return Envelope(code=0, message="ok", data=data)


@router.get("/status")
async def get_status(current_user: User = Depends(get_current_user)) -> Envelope:
    return Envelope(code=0, message="ok", data=_status_payload(current_user).model_dump())


@router.delete("/certification")
async def revoke_certification(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Envelope:
    current_user.qualified_investor = False
    current_user.investor_certified_at = None
    current_user.investor_tags = None

    session.add(current_user)
    session.commit()
    session.refresh(current_user)

    return Envelope(code=0, message="ok", data=_status_payload(current_user).model_dump())
