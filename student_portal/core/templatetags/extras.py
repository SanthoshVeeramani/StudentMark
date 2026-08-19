from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def attr(value, attr_name):
    return getattr(value, attr_name) if value else ""
