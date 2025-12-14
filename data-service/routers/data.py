from fastapi import APIRouter

from schemas.data import CleanRequest, CleanResponse
from services.data_service import clean_payload, summarize_payload

router = APIRouter()


@router.post("/clean", response_model=CleanResponse)
async def clean_data(payload: CleanRequest) -> CleanResponse:
    cleaned = clean_payload(payload)
    summary = summarize_payload(cleaned)
    return CleanResponse(**cleaned.model_dump(), summary=summary)


