import logging
import os
import psycopg2

DATABASE_URL = os.environ.get("DATABASE_URL")


def _ensure_database_url():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL environment variable is not set")


def create_tables(cur=None):
    """Create database tables if they do not exist.

    When *cur* is not provided, this function opens its own connection using
    a context manager. This allows other modules (e.g., application startup)
    to simply call ``create_tables()`` without managing connections.
    """

    _ensure_database_url()

    if cur is None:
        with psycopg2.connect(DATABASE_URL) as conn, conn.cursor() as cur:
            create_tables(cur)
        return

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS merchants (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL
        );
        """
    )
    cur.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS merchant_name_unique_idx ON merchants (LOWER(name));"
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS deals (
            id SERIAL PRIMARY KEY,
            title TEXT,
            price TEXT,
            original_price TEXT,
            discount TEXT,
            image_url TEXT,
            product_url TEXT,
            merchant_id INTEGER REFERENCES merchants(id),
            merchant_image TEXT,
            rating TEXT,
            reviews_count TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            duplicate_count INTEGER DEFAULT 0,
            UNIQUE (title, original_price, merchant_id)
        );
        """
    )

def insert_deals(deals_data):
    _ensure_database_url()
    with psycopg2.connect(DATABASE_URL) as conn, conn.cursor() as cur:
        create_tables(cur)

        for deal in deals_data["products"]:
            try:
                merchant_name = deal.get("merchant")
                if merchant_name:
                    cur.execute(
                        """
                        INSERT INTO merchants (name)
                        VALUES (%s)
                        ON CONFLICT (LOWER(name)) DO NOTHING;
                        """,
                        (merchant_name,),
                    )

                    cur.execute(
                        "SELECT id FROM merchants WHERE LOWER(name) = LOWER(%s);",
                        (merchant_name,),
                    )
                    merchant_id_result = cur.fetchone()
                    merchant_id = (
                        merchant_id_result[0] if merchant_id_result else None
                    )
                else:
                    merchant_id = None

                cur.execute(
                    """
                    INSERT INTO deals (title, price, original_price, discount, image_url, product_url, merchant_id, merchant_image, rating, reviews_count)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (title, original_price, merchant_id) DO UPDATE SET
                        price = EXCLUDED.price,
                        discount = EXCLUDED.discount,
                        image_url = EXCLUDED.image_url,
                        merchant_image = EXCLUDED.merchant_image,
                        rating = EXCLUDED.rating,
                        reviews_count = EXCLUDED.reviews_count,
                        updated_at = CURRENT_TIMESTAMP,
                        duplicate_count = deals.duplicate_count + 1;
                    """,
                    (
                        deal.get("title"),
                        deal.get("price"),
                        deal.get("original_price"),
                        deal.get("discount"),
                        deal.get("image_url"),
                        deal.get("product_url"),
                        merchant_id,
                        deal.get("merchant_image"),
                        deal.get("rating"),
                        deal.get("reviews_count"),
                    ),
                )
                logging.info(
                    f"Inserting/Updating deal: {deal.get('title')}, Rating: {deal.get('rating')}, Reviews: {deal.get('reviews_count')}"
                )
            except Exception as e:
                logging.error(f"Error inserting deal: {e}")
                conn.rollback()


def get_all_merchants():
    _ensure_database_url()
    with psycopg2.connect(DATABASE_URL) as conn, conn.cursor() as cur:
        cur.execute("SELECT name FROM merchants ORDER BY name")
        merchants = [row[0] for row in cur.fetchall()]
    return merchants

def get_deals_from_db(
    page: int = 1, page_size: int = 50, merchant: str = None
):
    _ensure_database_url()
    with psycopg2.connect(DATABASE_URL) as conn, conn.cursor() as cur:
        offset = (page - 1) * page_size

        count_query = (
            "SELECT COUNT(*) FROM deals d JOIN merchants m ON d.merchant_id = m.id"
        )
        params = []
        if merchant:
            count_query += " WHERE LOWER(m.name) = LOWER(%s)"
            params.append(merchant)

        cur.execute(count_query, tuple(params))
        total_products = cur.fetchone()[0]

        select_query = """
            SELECT d.*, m.name as merchant_name
            FROM deals d
            JOIN merchants m ON d.merchant_id = m.id
        """
        if merchant:
            select_query += " WHERE LOWER(m.name) = LOWER(%s)"

        select_query += " ORDER BY d.scraped_at DESC LIMIT %s OFFSET %s"
        params.extend([page_size, offset])

        cur.execute(select_query, tuple(params))
        deals = cur.fetchall()

    columns = [
        "id",
        "title",
        "price",
        "original_price",
        "discount",
        "image_url",
        "product_url",
        "merchant_id",
        "merchant_image",
        "rating",
        "reviews_count",
        "scraped_at",
        "updated_at",
        "duplicate_count",
        "merchant",
    ]

    deals_list = [dict(zip(columns, deal)) for deal in deals]

    return {
        "total_products": total_products,
        "products": deals_list,
        "page": page,
        "page_size": page_size,
    }
