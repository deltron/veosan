def to_lowercase(value):
    if value:
        return value.lower()
    else:
        return value

def escape_brackets(value):
    if value:
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')
        return value

def to_uppercase(value):
    if value:
        return value.upper()
    else:
        return value

def string_to_int(value):
    if value:
        return int(value)
    else:
        return value

def remove_spaces(value):
    if value:
        return value.replace(" ", "")
    else:
        return value
