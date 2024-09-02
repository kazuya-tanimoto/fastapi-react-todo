from unittest.mock import patch

import pytest
from motor import motor_asyncio
from utils.dependencies import connect_database


def test_connect_database_with_valid_key() -> None:
    with patch("utils.dependencies.config", return_value="mongodb://valid_key"):
        db = connect_database()
        assert db.name == "API_DB"


def test_connect_database_with_invalid_key() -> None:
    with patch("utils.dependencies.config", return_value="invalid_key"):
        with pytest.raises(motor_asyncio.InvalidURI):
            connect_database()


def test_connect_database_with_missing_key() -> None:
    with patch("utils.dependencies.config", side_effect=KeyError):
        with pytest.raises(KeyError):
            connect_database()
