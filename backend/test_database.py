import backend.database as db
from unittest.mock import MagicMock, patch


def test_insert_deals_commits_once_and_closes_connection():
    db.DATABASE_URL = "postgres://example"
    deals_data = {
        "products": [
            {
                "merchant": "Shop",
                "title": "Item",
                "price": "10",
                "original_price": "20",
                "discount": "50%",
                "image_url": "img",
                "product_url": "url",
                "merchant_image": "mi",
                "rating": "4",
                "reviews_count": "100",
            }
        ]
    }

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        (1,),
        (
            "Item",
            "10",
            "20",
            "50%",
            "img",
            "url",
            1,
            "mi",
            "4",
            "100",
        ),
    ]
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.__enter__.return_value = mock_conn

    def exit_func(exc_type, exc, tb):
        mock_conn.commit()

    mock_conn.__exit__.side_effect = exit_func

    with patch("backend.database.psycopg2.connect", return_value=mock_conn), \
         patch("backend.database.create_tables") as mock_create_tables, \
         patch("backend.database._ensure_database_exists"):
        db.insert_deals(deals_data)

    mock_create_tables.assert_called_once()
    mock_cursor.execute.assert_any_call(
        "TRUNCATE TABLE merchants RESTART IDENTITY;"
    )
    mock_cursor.execute.assert_any_call(
        "TRUNCATE TABLE deals RESTART IDENTITY CASCADE;"
    )
    mock_conn.commit.assert_called_once()
    mock_conn.__exit__.assert_called_once()
    mock_conn.cursor.return_value.__exit__.assert_called_once()


def test_insert_deals_avoids_duplicate_merchants():
    db.DATABASE_URL = "postgres://example"
    deals_data = {
        "products": [
            {
                "merchant": "Shop",
                "title": "Item1",
                "price": "10",
                "original_price": "20",
                "discount": "50%",
                "image_url": "img1",
                "product_url": "url1",
                "merchant_image": "mi1",
                "rating": "4",
                "reviews_count": "100",
            },
            {
                "merchant": "Shop",
                "title": "Item2",
                "price": "12",
                "original_price": "24",
                "discount": "50%",
                "image_url": "img2",
                "product_url": "url2",
                "merchant_image": "mi2",
                "rating": "5",
                "reviews_count": "200",
            },
        ]
    }

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchone.side_effect = [
        (1,),
        (
            "Item1",
            "10",
            "20",
            "50%",
            "img1",
            "url1",
            1,
            "mi1",
            "4",
            "100",
        ),
        (1,),
        (
            "Item2",
            "12",
            "24",
            "50%",
            "img2",
            "url2",
            1,
            "mi2",
            "5",
            "200",
        ),
    ]
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.__enter__.return_value = mock_conn

    with patch("backend.database.psycopg2.connect", return_value=mock_conn), patch(
        "backend.database.create_tables"
    ), patch("backend.database._ensure_database_exists"):
        db.insert_deals(deals_data)

    merchant_insert_calls = [
        c
        for c in mock_cursor.execute.call_args_list
        if "INSERT INTO merchants" in c.args[0]
    ]
    assert len(merchant_insert_calls) == 2
    for c in merchant_insert_calls:
        assert (
            "ON CONFLICT ON CONSTRAINT merchant_name_unique_idx DO NOTHING" in c.args[0]
        )


def test_merchants_sequence_reset():
    db.DATABASE_URL = "postgres://example"
    deals_data = {
        "products": [
            {
                "merchant": "Shop",
                "title": "Item",
                "price": "10",
                "original_price": "20",
                "discount": "50%",
                "image_url": "img",
                "product_url": "url",
                "merchant_image": "mi",
                "rating": "4",
                "reviews_count": "100",
            }
        ]
    }

    mock_conn_insert = MagicMock()
    mock_cursor_insert = MagicMock()
    mock_cursor_insert.fetchone.side_effect = [
        (1,),
        (
            "Item",
            "10",
            "20",
            "50%",
            "img",
            "url",
            1,
            "mi",
            "4",
            "100",
        ),
    ]
    mock_conn_insert.cursor.return_value.__enter__.return_value = mock_cursor_insert
    mock_conn_insert.__enter__.return_value = mock_conn_insert

    def exit_insert(exc_type, exc, tb):
        mock_conn_insert.commit()

    mock_conn_insert.__exit__.side_effect = exit_insert

    mock_conn_seq = MagicMock()
    mock_cursor_seq = MagicMock()
    mock_cursor_seq.fetchone.return_value = (1,)
    mock_conn_seq.cursor.return_value.__enter__.return_value = mock_cursor_seq
    mock_conn_seq.__enter__.return_value = mock_conn_seq

    with patch(
        "backend.database.psycopg2.connect", side_effect=[mock_conn_insert, mock_conn_seq]
    ), patch("backend.database._ensure_database_exists"):
        db.insert_deals(deals_data)
        last_value = db.get_merchants_last_value()

    assert last_value == 1
    mock_cursor_seq.execute.assert_called_once_with(
        "SELECT last_value FROM merchants_id_seq;"
    )


def test_get_deals_from_db_joins_merchants():
    db.DATABASE_URL = "postgres://example"
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.__enter__.return_value = mock_conn

    mock_cursor.fetchone.return_value = (1,)
    mock_cursor.fetchall.return_value = [
        (
            1,
            "Item",
            "10",
            "20",
            "50%",
            "img",
            "url",
            1,
            "mi",
            "4",
            "100",
            None,
            None,
            "Shop",
        )
    ]

    with patch("backend.database.psycopg2.connect", return_value=mock_conn), patch(
        "backend.database._ensure_database_exists"
    ):
        result = db.get_deals_from_db()

    executed_queries = [call.args[0] for call in mock_cursor.execute.call_args_list]
    assert any(
        "LEFT JOIN merchants m ON d.merchant_id = m.id" in query
        for query in executed_queries
    )
    assert result["products"][0]["merchant"] == "Shop"
