def clear_string(string: str, exclude_list: list = None):
    if exclude_list is None:
        exclude_list = list()

    patterns_to_be_cleaned = [
        '.',
        '-',
        '/',
        '/',
        '(',
        ')',
        '+',
        ' ',
    ]

    if not string:
        return string

    for pattern in patterns_to_be_cleaned:
        if pattern not in exclude_list:
            string = string.replace(pattern, '')

    return string


def represents_int(s) -> bool:
    try:
        int(s)
        return True
    except ValueError:
        return False


def random_string() -> str:
    """Generate a random string of fixed length """
    import uuid
    return uuid.uuid4().hex
