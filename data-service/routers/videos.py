"""
视频中心 API
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, File, Form, Header, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from core.config import settings
from core.database import get_async_session
from models.video import Video
from schemas.video import VideoListResponse, VideoItem

router = APIRouter(prefix="/videos", tags=["videos"])

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm"}
ALLOWED_COVER_TYPES = {"image/jpeg", "image/png", "image/webp"}


def _safe_filename(original: str, default_ext: str) -> str:
    suffix = Path(original).suffix.lower().strip()
    if not suffix or not re.match(r"^\.[a-z0-9]+$", suffix):
        suffix = default_ext
    return f"{uuid4().hex}{suffix}"


def _resolve_dir(relative_path: str) -> Path:
    base_dir = Path(__file__).resolve().parents[1]
    return (base_dir / relative_path).resolve()


def _ensure_within(base_dir: Path, target_path: Path) -> None:
    try:
        target_path.relative_to(base_dir)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="非法文件路径")


def _file_url(static_root: Path, file_path: Path) -> str:
    relative = file_path.relative_to(static_root).as_posix()
    return f"/api/static/{relative}"


def _require_admin(x_user_role: Optional[str] = Header(None, alias="X-User-Role")) -> None:
    if not x_user_role:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="缺少认证信息")
    if x_user_role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限访问")


async def _save_upload_file(
    upload: UploadFile,
    target_dir: Path,
    max_size_bytes: int,
    allowed_types: set[str],
    default_ext: str,
) -> Path:
    if upload.content_type not in allowed_types:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="不支持的文件类型")

    target_dir.mkdir(parents=True, exist_ok=True)
    filename = _safe_filename(upload.filename or "", default_ext)
    target_path = (target_dir / filename).resolve()
    _ensure_within(target_dir, target_path)

    size = 0
    with open(target_path, "wb") as buffer:
        while True:
            chunk = await upload.read(1024 * 1024)
            if not chunk:
                break
            size += len(chunk)
            if size > max_size_bytes:
                buffer.close()
                if target_path.exists():
                    target_path.unlink(missing_ok=True)
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="文件过大")
            buffer.write(chunk)

    await upload.close()
    return target_path


@router.get("", response_model=VideoListResponse, summary="获取视频列表")
async def list_videos(
    db_session: AsyncSession = Depends(get_async_session),
):
    stmt = select(Video).order_by(Video.created_at.desc())
    result = await db_session.execute(stmt)
    items = result.scalars().all()
    return {
        "items": [
            VideoItem(
                id=item.id,
                title=item.title,
                description=item.description,
                url=item.url,
                cover_url=item.cover_url,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in items
        ]
    }


@router.post("", response_model=VideoItem, summary="上传视频（管理员）")
async def upload_video(
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    cover: Optional[UploadFile] = File(None),
    _: None = Depends(_require_admin),
    db_session: AsyncSession = Depends(get_async_session),
):
    max_size_bytes = int(settings.video_max_size_mb) * 1024 * 1024
    video_dir = _resolve_dir(settings.video_upload_dir)
    cover_dir = _resolve_dir(settings.video_cover_dir)

    video_path = await _save_upload_file(
        upload=file,
        target_dir=video_dir,
        max_size_bytes=max_size_bytes,
        allowed_types=ALLOWED_VIDEO_TYPES,
        default_ext=".mp4",
    )

    cover_path = None
    if cover is not None:
        try:
            cover_path = await _save_upload_file(
                upload=cover,
                target_dir=cover_dir,
                max_size_bytes=10 * 1024 * 1024,
                allowed_types=ALLOWED_COVER_TYPES,
                default_ext=".png",
            )
        except Exception:
            if video_path.exists():
                try:
                    video_path.unlink()
                except Exception:
                    pass
            raise

    static_root = _resolve_dir("static")
    video_url = _file_url(static_root, video_path)
    cover_url = _file_url(static_root, cover_path) if cover_path else None

    new_video = Video(
        title=title,
        description=description,
        url=video_url,
        cover_url=cover_url,
        file_path=str(video_path),
        cover_path=str(cover_path) if cover_path else None,
    )
    db_session.add(new_video)
    await db_session.commit()
    await db_session.refresh(new_video)

    return VideoItem(
        id=new_video.id,
        title=new_video.title,
        description=new_video.description,
        url=new_video.url,
        cover_url=new_video.cover_url,
        created_at=new_video.created_at,
        updated_at=new_video.updated_at,
    )


@router.delete("/{video_id}", summary="删除视频（管理员）")
async def delete_video(
    video_id: int,
    _: None = Depends(_require_admin),
    db_session: AsyncSession = Depends(get_async_session),
):
    stmt = select(Video).where(Video.id == video_id)
    result = await db_session.execute(stmt)
    video = result.scalars().first()
    if not video:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="视频不存在")

    video_path = Path(video.file_path)
    cover_path = Path(video.cover_path) if video.cover_path else None

    static_root = _resolve_dir("static")
    for path in [video_path, cover_path]:
        if path is None:
            continue
        try:
            _ensure_within(static_root, path.resolve())
        except HTTPException:
            continue
        if path.exists():
            try:
                path.unlink()
            except Exception:
                pass

    await db_session.delete(video)
    await db_session.commit()

    return {"success": True}
