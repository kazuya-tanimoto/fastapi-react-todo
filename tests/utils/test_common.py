from utils.common import convert_document


def test_convert_document_with_valid_fields() -> None:
    document = {"_id": "507f1f77bcf86cd799439011", "name": "John", "age": 30}
    fields = ["_id", "name"]
    result = convert_document(document, fields)
    assert result == {"id": "507f1f77bcf86cd799439011", "name": "John"}


def test_convert_document_with_missing_fields() -> None:
    document = {"_id": "507f1f77bcf86cd799439011", "name": "John"}
    fields = ["_id", "age"]
    result = convert_document(document, fields)
    assert result == {"id": "507f1f77bcf86cd799439011"}


def test_convert_document_with_empty_fields() -> None:
    document = {"_id": "507f1f77bcf86cd799439011", "name": "John", "age": 30}
    fields = []
    result = convert_document(document, fields)
    assert result == {}
