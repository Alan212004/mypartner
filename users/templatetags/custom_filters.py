from django import template

register = template.Library()

@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class": css_class})


@register.filter
def attr(field, attrs):
    """
    Add attributes to form fields. 
    attrs should be a string like "placeholder:Enter your first name".
    """
    attrs_dict = {}
    for attr in attrs.split(','):
        key, value = attr.split(':')
        attrs_dict[key.strip()] = value.strip()

    if hasattr(field, 'widget'):
        for key, value in attrs_dict.items():
            field.widget.attrs[key] = value
        return field
    return field  # Return the original field if it has no widget.

@register.filter
def get_item(lst, index):
    """Get an item from a list by index."""
    return lst[index] if index < len(lst) else None