from django import template

register = template.Library()

@register.filter
def separator(price):
    return "{:,}".format(price)