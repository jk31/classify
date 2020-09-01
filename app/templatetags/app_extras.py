# {% load app_extras %}
from django import template

register = template.Library()

@register.filter
def saved_only(value):
    """Returns only saved models"""
    return value.filter(saved=True)

@register.filter
def to_100(value):
    """Multiply number with 100"""
    return float(value)*100

