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
        "TRUNCATE TABLE deals RESTART IDENTITY CASCADE;"
    )
    mock_conn.commit.assert_called_once()
    mock_conn.__exit__.assert_called_once()
    mock_conn.cursor.return_value.__exit__.assert_called_once()
