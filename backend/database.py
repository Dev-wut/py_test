import os
import psycopg2
import json
import logging

DATABASE_URL = os.environ.get("DATABASE_URL")

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def create_deals_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id SERIAL PRIMARY KEY,
            title TEXT,
            price TEXT,
            original_price TEXT,
            discount TEXT,
            image_url TEXT,
            product_url TEXT UNIQUE,
            merchant TEXT,
            merchant_image TEXT,
            rating TEXT,
            reviews_count TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def insert_deals(deals_data):
    conn = get_db_connection()
    cur = conn.cursor()
    create_deals_table()

    for deal in deals_data["products"]:
        try:
            cur.execute("""
                INSERT INTO deals (title, price, original_price, discount, image_url, product_url, merchant, merchant_image, rating, reviews_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_url) DO UPDATE SET
                    title = EXCLUDED.title,
                    price = EXCLUDED.price,
                    original_price = EXCLUDED.original_price,
                    discount = EXCLUDED.discount,
                    image_url = EXCLUDED.image_url,
                    merchant = EXCLUDED.merchant,
                    merchant_image = EXCLUDED.merchant_image,
                    rating = EXCLUDED.rating,
                    reviews_count = EXCLUDED.reviews_count,
                    scraped_at = CURRENT_TIMESTAMP;
            """, (
                deal.get("title"),
                deal.get("price"),
                deal.get("original_price"),
                deal.get("discount"),
                deal.get("image_url"),
                deal.get("product_url"),
                deal.get("merchant"),
                deal.get("merchant_image"),
                deal.get("rating"),
                deal.get("reviews_count")
            ))
        except Exception as e:
            logging.error(f"Error inserting deal: {e}")
            conn.rollback()
        else:
            conn.commit()

    cur.close()
    conn.close()

def get_deals_from_db(page: int = 1, page_size: int = 50):
    conn = get_db_connection()
    cur = conn.cursor()
    
    offset = (page - 1) * page_size
    
    cur.execute("SELECT COUNT(*) FROM deals")
    total_products = cur.fetchone()[0]
    
    cur.execute("SELECT * FROM deals ORDER BY scraped_at DESC LIMIT %s OFFSET %s", (page_size, offset))
    deals = cur.fetchall()
    
    cur.close()
    conn.close()
    
    columns = [
        "id", "title", "price", "original_price", "discount", 
        "image_url", "product_url", "merchant", "merchant_image", 
        "rating", "reviews_count", "scraped_at"
    ]
    
    deals_list = [dict(zip(columns, deal)) for deal in deals]
    
    return {
        "total_products": total_products,
        "products": deals_list,
        "page": page,
        "page_size": page_size
    }
