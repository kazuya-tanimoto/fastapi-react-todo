def serialize(document, fields) -> dict:
    serialized = {}
    for field in fields:
        if field == '_id':
            serialized['id'] = str(document['_id'])
        else:
            serialized[field] = document[field]
    return serialized