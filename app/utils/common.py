def convert_document(document: dict, fields: list[str]) -> dict:
    """
    ドキュメントから指定されたフィールドを抽出し、_idをidに変換する

    :param document: MongoDBドキュメント
    :param fields: 抽出するフィールドのリスト
    :return: 変換されたドキュメントの辞書
    """
    serialized = {}
    for field in fields:
        if field == "_id":
            serialized["id"] = str(document["_id"])
        elif field in document:
            serialized[field] = document[field]
    return serialized
