"""Configuration constants for scraper defaults."""


DEFAULT_SCRAPER_CONFIG = {
    "base_url": "https://www.priceza.com",
    "selectors": {
        "load_more_button": {"class": "hotdeal-tab__load-more__btn"},
        "hot_deals_container": {
            "tag": "div",
            "class": "pz-pdb-section",
            "id": "home-specials",
        },
        "product_item": {"tag": "div", "class": "pz-pdb-item"},
        "title": {"tag": "h3", "class": "pz-pdb_name"},
        "original_price": {"tag": "del", "class": "pz-base-price"},
        "price": {"tag": "span", "class": "pz-pdb-price"},
        "discount": {"tag": "div", "class": "pz-label--discount"},
        "image": {"tag": "img", "class": "pz-pdb_media--img"},
        "merchant_image": {"tag": "img", "class": "pz-pdb_store--img"},
        "product_link": {
            "tag": "a",
            "attrs": {"href": True, "onmousedown": True},
        },
        "rating": {"tag": "div", "class": "pz-rating-score-text"},
    },
    "json_keys": {
        "title": "title",
        "price": "price",
        "original_price": "original_price",
        "discount": "discount",
        "image_url": "image_url",
        "product_url": "product_url",
        "merchant": "merchant",
        "merchant_image": "merchant_image",
        "rating": "rating",
        "reviews_count": "reviews_count",
    },
}

