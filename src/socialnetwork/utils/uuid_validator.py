import uuid

# https://stackoverflow.com/questions/53847404/how-to-check-uuid-validity-in-python


def check_uuid_valid(uuid_str: str) -> bool:
    """Used to distinguish between UUID and FQID"""
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False
