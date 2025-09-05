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
            scraped_at TIMESTAMPTZ DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Bangkok'),
            updated_at TIMESTAMPTZ DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Asia/Bangkok')
        );
        """
    )


def insert_deals(deals_data):
    _ensure_database_url()
    with psycopg2.connect(DATABASE_URL) as conn, conn.cursor() as cur:
        create_tables(cur)
        # Clear existing data
        cur.execute("TRUNCATE TABLE merchants RESTART IDENTITY CASCADE;")
        cur.execute("TRUNCATE TABLE deals RESTART IDENTITY CASCADE;")

        # Insert merchants first to ensure fresh IDs
        for deal in deals_data["products"]:
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

        for deal in deals_data["products"]:
            try:
                merchant_name = deal.get("merchant")
                if merchant_name:
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
                    INSERT INTO deals (
                        title,
                        price,
                        original_price,
                        discount,
                        image_url,
                        product_url,
                        merchant_id,
                        merchant_image,
                        rating,
                        reviews_count
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING title, price, original_price, discount, image_url, product_url, merchant_id, merchant_image, rating, reviews_count;
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
                returned_row = cur.fetchone()
                if returned_row:
                    db_fields = [
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
                    ]
                    db_deal = dict(zip(db_fields, returned_row))
                    mismatches = {}
                    for field in db_fields:
                        expected_value = (
                            merchant_id if field == "merchant_id" else deal.get(field)
                        )
                        if db_deal.get(field) != expected_value:
                            mismatches[field] = {
                                "db": db_deal.get(field),
                                "scraped": expected_value,
                            }
                    if mismatches:
                        logging.warning(
                            f"Mismatch for deal {deal.get('title')}: {mismatches}"
                        )
                logging.info(
                    f"Inserting deal: {deal.get('title')}, Rating: {deal.get('rating')}, Reviews: {deal.get('reviews_count')}"
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


def get_merchants_last_value():
    """Return the current value of the merchants ID sequence."""
    _ensure_database_url()
    with psycopg2.connect(DATABASE_URL) as conn, conn.cursor() as cur:
        cur.execute("SELECT last_value FROM merchants_id_seq;")
        return cur.fetchone()[0]


def get_deals_from_db(
    page: int = 1, page_size: int = 50, merchant: str = None, title: str = None
):
    _ensure_database_url()
    with psycopg2.connect(DATABASE_URL) as conn, conn.cursor() as cur:
        offset = (page - 1) * page_size

        count_query = (
            "SELECT COUNT(*) FROM deals d LEFT JOIN merchants m ON d.merchant_id = m.id"
        )
        params = []
        if merchant:
            count_query += " WHERE LOWER(m.name) = LOWER(%s)"
            params.append(merchant)
        if title:
            if "WHERE" in count_query:
                count_query += " AND LOWER(d.title) LIKE LOWER(%s)"
            else:
                count_query += " WHERE LOWER(d.title) LIKE LOWER(%s)"
            params.append(f"%{title}%")

        cur.execute(count_query, tuple(params))
        total_products = cur.fetchone()[0]

        select_query = """
            SELECT d.*, COALESCE(m.name, '') AS merchant
            FROM deals d
            LEFT JOIN merchants m ON d.merchant_id = m.id
        """
        if merchant:
            select_query += " WHERE LOWER(m.name) = LOWER(%s)"
        if title:
            if "WHERE" in select_query:
                select_query += " AND LOWER(d.title) LIKE LOWER(%s)"
            else:
                select_query += " WHERE LOWER(d.title) LIKE LOWER(%s)"

        select_query += " ORDER BY d.id DESC LIMIT %s OFFSET %s"
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
        "merchant",
    ]

    deals_list = [dict(zip(columns, deal)) for deal in deals]
    for deal in deals_list:
        merchant_value = deal.get("merchant")
        deal["merchant"] = str(merchant_value) if merchant_value is not None else ""

    return {
        "total_products": total_products,
        "products": deals_list,
        "page": page,
        "page_size": page_size,
    }
