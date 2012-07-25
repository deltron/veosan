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