from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

# This will hold the details of the recent post
post = []

# Websites to scrape
websites = [
    # "https://beincrypto.com/news",
    "https://www.coingecko.com/en/news",
    "https://www.coingecko.com/",
    # "https://www.coindesk.com/feed",
]


def news_scrapper():
    """
    This scrapes the most recent post
    """
    site = websites[0]
    headers = {"User-Agent": "Mozilla/5.0"}
    req = Request(site, headers=headers)
    page = urlopen(req)
    soup = BeautifulSoup(page, features="lxml")

    articles = soup.find_all("div", attrs={"class": "my-4"})
    article_pic = soup.find("div", attrs={"class": "float-left post-thumbnail"})
    recent_post = articles[0]  # Gets the first article
    title = recent_post.header.h2.a
    author = soup.find("span", attrs={"class": "font-weight-bold"})
    post_body = soup.find("div", attrs={"class": "post-body"})
    post.append(title.text.split())
    post.append(article_pic.img.get("src")) # type:ignore
    post.append(author.text.split())  # type:ignore
    post.append(post_body.text.split())  # type:ignore
    return post

def price_list_scrapper():
    names = []
    prices = []
    site = websites[1]
    headers = {"User-Agent": "Mozilla/5.0"}
    req = Request(site, headers=headers)
    page = urlopen(req)
    soup = BeautifulSoup(page, features="lxml")

    price_list = soup.find("tbody", attrs={"data-target":"currencies.contentBox"})
    prices_item_name = price_list.find_all("td", attrs={"class":"py-0 coin-name cg-sticky-col cg-sticky-third-col px-0"}) #type:ignore
    prices_list = price_list.find_all('div',attrs={"class":"tw-flex-1"}) #type:ignore
    for price in prices_item_name:
        names.append(price.text.strip())
    for price in prices_list:
        prices.append(price.text.split())
    res = {names[i]: prices[i] for i in range(len(names))}
    return res
    # print(len(prices))

# price_list_scrapper()
    