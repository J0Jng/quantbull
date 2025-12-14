from schemas.data import CleanRequest, CleanResponse


def clean_payload(payload: CleanRequest) -> CleanRequest:
    # Pretend to strip unwanted fields and normalize casing
    normalized_tags = [tag.lower().strip() for tag in payload.tags]
    return CleanRequest(
        source=payload.source.strip(),
        content=payload.content.strip(),
        tags=normalized_tags,
    )


def summarize_payload(payload: CleanRequest) -> str:
    words = len(payload.content.split())
    return f"{payload.source} payload accepted with {words} words and {len(payload.tags)} tags."


