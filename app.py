from datetime import datetime
from flask import Flask, render_template, Blueprint
from flask_caching import Cache
from jmenu.main import get_version
from jmenu.api import fetch_restaurant_items
from jmenu.classes import RESTAURANTS

cache = Cache(
    config={
        "CACHE_TYPE": "SimpleCache",
        "CACHE_DEFAULT_TIMEOUT": 3 * 60 * 60,
    }
)


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


routes = Blueprint("route", __name__)


@routes.route("/")
@cache.cached()
def get_menu():
    data = JmenuData()
    return render_template("menu.html", data=data)


app = Flask(__name__)
app.register_blueprint(routes)
cache.init_app(app)
