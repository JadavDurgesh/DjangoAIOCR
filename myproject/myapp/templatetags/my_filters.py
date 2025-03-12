from django import template

register = template.Library()

@register.filter
def get_item(value, key):
    if isinstance(value, dict):
        return value.get(key, "")
    return value  # Return the value directly if not a dict
