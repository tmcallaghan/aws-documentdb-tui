def truncate(s: str, maxlen: int) -> str:
    if len(s) <= maxlen:
        return s
    if maxlen <= 3:
        return s[:maxlen]
    return s[: maxlen - 3] + "..."
