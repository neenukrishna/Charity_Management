# charity/templatetags/charity_extras.py
from django import template

register = template.Library()

@register.filter
def replace_newlines(value):
    """
    Replace any newline or carriage-return characters with a space.
    """
    if not value:
        return ''
    return value.replace('\n', ' ').replace('\r', ' ')
