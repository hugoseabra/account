import uuid


def get_validated_uuid_from_string(uuid_str: str):
    valid_uuid = None
    if uuid_str:
        try:
            uuid.UUID(uuid_str)
            valid_uuid = uuid_str
        except ValueError:
            pass

    return valid_uuid
