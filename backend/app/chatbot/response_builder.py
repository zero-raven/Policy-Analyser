def build_response(
    answer: str,
    response_type: str,
    sources: list[str] | None = None,
    risks: dict | None = None
) -> dict:
    return {
        "answer": answer,
        "type": response_type,
        "sources": sources or [],
        "risks": risks or {}
    }
