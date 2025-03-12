import json
from django import template

register = template.Library()

@register.filter
def json_pretty(value):
    """Pretty prints JSON data."""
    try:
        return json.dumps(value, indent=4)
    except Exception:
        return value
