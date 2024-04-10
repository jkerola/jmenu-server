from datetime import datetime
from flask import Flask, render_template, Blueprint
from flask_caching import Cache
from jmenu.main import get_version
from jmenu.api import fetch_restaurant_items
from jmenu.classes import RESTAURANTS
import feedparser


cache = Cache(
    config={
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 3 * 60 * 60,
    }
)

yle_rss = "https://feeds.yle.fi/uutiset/v1/majorHeadlines/YLE_UUTISET.rss"
uni_rss = "https://www.oulu.fi/fi/rss/article/10330215-e23f-4535-9f56-51771405d962/all"


class JmenuData:
    def __init__(self):
        fetch_date = datetime.now()
        self.menus_fi = {
            res.name: fetch_restaurant_items(res, fetch_date=fetch_date, lang_code="fi")
            for res in RESTAURANTS
        }
        self.menus_en = {
            res.name: fetch_restaurant_items(res, fetch_date=fetch_date, lang_code="en")
            for res in RESTAURANTS
        }
        self.version = get_version()
        self.timestamp = fetch_date.strftime("%d.%m.%y at %H:%M:%S")
        self.date = fetch_date.strftime("%d.%m")


class NewsData:
    def __init__(self, source: str, feed: str):
        self.items = parse_rss(feed)
        self.source = source


routes = Blueprint("route", __name__)


def parse_rss(feed: str, slice: int = 5) -> list[dict]:
    news_items = feedparser.parse(feed)
    for item in news_items.entries:
        item.published = datetime(*(item.published_parsed[0:6])).strftime(
            "%d.%m.%y %H:%M"
        )
    news_items.entries.sort(key=lambda x: x["published_parsed"], reverse=True)
    return news_items.entries[:slice]


@routes.route("/")
@cache.cached()
def get_menu():
    data = JmenuData()
    return render_template("menu.html", data=data)


@routes.route("/news")
@cache.cached(timeout=30 * 60)
def get_news():
    data = [
        NewsData("Yle Uutiset", yle_rss),
        NewsData("Oulun Yliopisto", uni_rss),
    ]

    return render_template("news.html", data=data)


app = Flask(__name__)
app.register_blueprint(routes)
cache.init_app(app)
