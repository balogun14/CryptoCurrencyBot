from typing import List
from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

# Websites to scrape from
websites = [
    "https://www.coingecko.com/en/news",
    "https://www.coingecko.com/",
]


def news_scrapper() -> List[str]:
    """
     This scrapes the most recent post from
     the first website and returns a list of strings.
      \n@required:  website:`str`:site to scrape from.
    """
    post: List[str] = []
    site: str = websites[0]
    headers: dict[str, str] = {"User-Agent": "Mozilla/5.0"}
    req: Request = Request(site, headers=headers)
    page = urlopen(req)
    soup = BeautifulSoup(page, features="lxml")
    # The parsed data
    articles = soup.find_all("div", attrs={"class": "my-4"})
    article_pic = soup.find("div", attrs={"class": "float-left post-thumbnail"})
    recent_post = articles[0]  # Gets the first article
    title = recent_post.header.h2.a
    post_body = soup.find("div", attrs={"class": "post-body"})
    first_paragraph: str = post_body.text.split(".")[0]  # type:ignore
    post.append(title.text)  # type:ignore
    post.append(article_pic.img.get("src"))  # type:ignore
    post.append(first_paragraph + " .")  # type:ignore
    return post


def price_list_scrapper():
    names = []
    prices = []
    site = websites[1]
    headers = {"User-Agent": "Mozilla/5.0"}
    req = Request(site, headers=headers)
    page = urlopen(req)
    soup = BeautifulSoup(page, features="lxml")

    price_list = soup.find("tbody", attrs={"data-target": "currencies.contentBox"})
    prices_item_name = price_list.find_all(  # type:ignore
        "td", attrs={"class": "py-0 coin-name cg-sticky-col cg-sticky-third-col px-0"}
    )  # type:ignore
    prices_list = price_list.find_all(  # type:ignore
        "div", attrs={"class": "tw-flex-1"}
    )  # type:ignore
    for price in prices_item_name:
        names.append(price.text.split())
    for price in prices_list:
        prices.append(price.text.split())
    res = {names[i]: prices[i] for i in range(len(names))}
    return res
