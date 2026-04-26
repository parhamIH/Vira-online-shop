from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the arg and the value"""
    return value * arg 