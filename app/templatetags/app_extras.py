# {% load app_extras %}
from django import template

register = template.Library()

@register.filter
def saved_only(value):
    """Returns only saved models"""
    return value.filter(saved=True)

