from django import template

register = template.Library()

@register.simple_tag
def range_filter(value):
    return range(value)
