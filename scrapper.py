from bs4 import BeautifulSoup
from urllib.request import Request, urlopen

# This will hold the details of the recent post
post = []

# Websites to scrape
websites = [
    # "https://beincrypto.com/news",
    "https://www.coingecko.com/en/news",
    # "https://www.coindesk.com/feed",
]


def scrapper():
    """
    This crpes the most recent post
    """
    site = websites[0]
    headers = {"User-Agent": "Mozilla/5.0"}
    req = Request(site, headers=headers)
    page = urlopen(req)
    soup = BeautifulSoup(page, features="lxml")

    articles = soup.find_all("div", attrs={"class": "my-4"})
    recent_post = articles[1]  # Gets the first article
    title = recent_post.header.h2.a
    author = soup.find("span", attrs={"class": "font-weight-bold"})
    post_body = soup.find("div", attrs={"class": "post-body"})
    post.append(title.text)
    post.append(author.text)
    post.append(post_body.text)
    return post


# length = len(post_body.text)


# for i in range(0,len(post)):
#     print(post[i])

#     print("------------------------------------")
