import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


ARCHIVE_URL = "https://web.archive.org/web/20230903112115/https://iz.ru/news"
SITE_ROOT = "https://iz.ru"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}


def load_page(url: str) -> str | None:
    """Загружает HTML-страницу, возвращает текст или None при ошибке."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
    except requests.exceptions.RequestException as err:
        print(f"Не удалось выполнить запрос: {err}")
        return None

    if resp.status_code == 404:
        print("Ошибка 404: страница не найдена")
        return None

    if resp.status_code != 200:
        print(f"Неожиданный статус ответа: {resp.status_code}")
        return None

    return resp.text


def parse_news(html: str) -> dict:
    """
    Парсит новости с архивной страницы iz.ru/news.
    Результат: словарь {раздел: [ {title, link}, ... ]}.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Блоки новостей
    news_blocks = soup.find_all(
        "div",
        class_="node__cart__item show_views_and_comments",
    )

    if not news_blocks:
        print("На странице не найдено ни одной новости.")
        return {}

    grouped_news: dict[str, list[dict]] = {}

    for block in news_blocks:
        # раздел (рубрика)
        section_node = block.find("a")
        section_name = section_node.get_text(strip=True) if section_node else "Без раздела"

        # заголовок
        title_node = block.find(
            "div",
            class_="node__cart__item__inside__info__title small-title-style1",
        )
        title_text = title_node.get_text(strip=True) if title_node else None

        # ссылка на новость
        link_node = block.find("a", class_="node__cart__item__inside")
        href_raw = link_node.get("href") if link_node else None

        if not title_text or not href_raw:
            # если чего-то важного нет, пропускаем
            continue

        # делаем ссылку абсолютной
        if href_raw.startswith("/"):
            full_link = urljoin(SITE_ROOT, href_raw)
        else:
            full_link = href_raw

        # добавляем в результат
        if section_name not in grouped_news:
            grouped_news[section_name] = []

        grouped_news[section_name].append(
            {
                "title": title_text,
                "link": full_link,
            }
        )

    return grouped_news


def main() -> None:
    html = load_page(ARCHIVE_URL)
    if html is None:
        return

    news = parse_news(html)

    if not news:
        print("Не удалось извлечь данные о новостях.")
    else:
        print(news)


if __name__ == "__main__":
    main()
