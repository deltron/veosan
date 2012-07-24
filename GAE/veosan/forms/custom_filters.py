import re


def to_lowercase(value):
    if value:
        return value.lower()
    else:
        return value

def escape_brackets(value):
    if value:
        #replace_left = value.replace('not', 'zot')
        #replace_right = replace_left.replace('>', ')')
        return re.sub('not','zot',value)