from bs4 import BeautifulSoup


URLS = [
    "https://example.com",
    "https://www.python.org",
    "https://docs.python.org/3/",
]


def get_title(html: str) -> str:
    title = BeautifulSoup(html, "html.parser").title
    return title.get_text(strip=True) if title else "Без заголовка"

