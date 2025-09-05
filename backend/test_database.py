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
         patch("backend.database.create_tables") as mock_create_tables:
        db.insert_deals(deals_data)

    mock_create_tables.assert_called_once()
    mock_cursor.execute.assert_any_call(
        "TRUNCATE TABLE merchants RESTART IDENTITY CASCADE;"
    )
    mock_cursor.execute.assert_any_call(
        "TRUNCATE TABLE deals RESTART IDENTITY CASCADE;"
    )
    mock_conn.commit.assert_called_once()
    mock_conn.__exit__.assert_called_once()
    mock_conn.cursor.return_value.__exit__.assert_called_once()


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

    with patch("backend.database.psycopg2.connect", side_effect=[mock_conn_insert, mock_conn_seq]):
        db.insert_deals(deals_data)
        last_value = db.get_merchants_last_value()

    assert last_value == 1
    mock_cursor_seq.execute.assert_called_once_with(
        "SELECT last_value FROM merchants_id_seq;"
    )
