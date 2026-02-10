from datetime import datetime, timezone

def utcnow() -> datetime:
    """
        Always return timezone-aware UTC datetime.
        Do NOT strip tzinfo — comparisons depend on this.
        """
    return datetime.now(timezone.utc)