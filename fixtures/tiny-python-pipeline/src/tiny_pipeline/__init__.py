def parse_rows(text: str) -> list[dict[str, str]]:
    lines=[l.strip() for l in text.splitlines() if l.strip()]
    if not lines: return []
    header=lines[0].split(',')
    return [dict(zip(header, line.split(','))) for line in lines[1:]]
