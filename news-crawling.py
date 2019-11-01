# %%
import uuid
import pickledb
from pathlib import Path
from typing import List
import newspaper
import requests
from tqdm import tqdm

# %%
# list news will be crawled
news = [
    ("detik.com", "https://www.detik.com/"),
    ("kontan.co.id", "https://kontan.co.id/"),
    ("cnnindonesia.com", "https://www.cnnindonesia.com/"),
    ("antaranews.com", "https://www.antaranews.com/"),
    ("bisnis.com", "https://www.bisnis.com/"),
    ("kompas.com", "https://www.kompas.com/"),
    ("republika.co.id", "https://republika.co.id"),
    ("liputan6.com", "https://www.liputan6.com/"),
    ("suara.com", "https://www.suara.com/"),
    ("tribunnews.com", "https://www.tribunnews.com"),
]


# %%
# get all article url
def generate_link(news_url: str) -> List[str]:
    """Generate link from news

    Args:
        news_url: url news ex: detik.com, kontan.co.id

    Returns:
        List of article
    """
    source = newspaper.build(news_url, memoize_articles=False)
    return source.article_urls()


article_url = []
for domain, url_article in tqdm(news):
    link = generate_link(url_article)
    article_url.append((domain, link))

# %%
# print total article fetch
for domain, item in article_url:
    print(f"{domain}: {len(item)}")

# %%
# get page info
session = requests.Session()


def get_html(url: str) -> str:
    """read url and return html

    Args:
        url: url will be get

    Returns:
        str html
    """
    r = session.get(url)
    if r.status_code != 200:
        return ''
    return r.text


def write_html(html: str, directory="news") -> str:
    """write html to file

    Args:
        html: str html will be write
        directory: target directory for save file

    Returns:
        filename generated
    """
    filename = str(uuid.uuid4())
    path = Path(directory) / filename
    with path.open("w") as file:
        file.write(html)
    return filename


db = pickledb.load('mapping.db', False)


def save_and_write(url: str, rewrite=True):
    if not rewrite:
        exist = db.get(url)
        if exist:
            return

    html = get_html(url)
    if not html:
        return

    filename = write_html(html)
    db.set(url, filename)


for d, item in article_url[:1]:
    for i in tqdm(item):
        save_and_write(i)
