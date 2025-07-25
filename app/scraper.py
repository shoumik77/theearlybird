import feedparser
from datetime import datetime
from app.schemas import ProductCreate
from app.crud import create_product, get_product_by_url

import requests
import feedparser
from datetime import datetime
from .schemas import ProductCreate

def parse_product_hunt_feed():
    url = "https://www.producthunt.com/feed"
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; TrendExplorerBot/1.0; +https://yourappurl.com)"
    }

    response = requests.get(url, headers=headers)
    feed = feedparser.parse(response.content)

    print(f"Fetched {len(feed.entries)} entries from Product Hunt RSS")

    products = []
    for entry in feed.entries:
        name = entry.title
        description = entry.description
        product_url = entry.link
        pub_date = datetime(*entry.published_parsed[:6])

        products.append(ProductCreate(
            name=name,
            description=description,
            url=product_url,
            tage=None,
            launch_date=pub_date.date()
        ))

    return products


def sync_new_products(db):
    products = parse_product_hunt_feed()
    new_count = 0
    for product in products:
        if get_product_by_url(db, product.url) is None:
            create_product(db, product)

            new_count += 1
    
    print(f"Synced {new_count} new products")
            

