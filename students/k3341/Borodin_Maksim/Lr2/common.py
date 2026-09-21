LIMIT = 10_000_000_000_000
WORKERS = 4


def split_range(limit: int = LIMIT, parts: int = WORKERS) -> list[tuple[int, int]]:
    """Разбивает диапазон 1..limit на почти равные части."""
    step = limit // parts
    ranges = []
    for index in range(parts):
        start = index * step + 1
        end = limit if index == parts - 1 else (index + 1) * step
        ranges.append((start, end))
    return ranges

