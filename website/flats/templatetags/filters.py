from django import template

register = template.Library()


@register.filter
def replace_n(value):
    return value.replace('\\n', '. ') if value else value
