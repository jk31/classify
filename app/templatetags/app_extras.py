import re

from django import template
from django.utils.safestring import mark_safe


register = template.Library()

@register.filter
def saved_only(value):
    """Returns only saved models"""
    return value.filter(saved=True)

@register.filter
def to_100(value):
    """Multiply number with 100"""
    return float(value)*100

@register.filter
def bootstrap_form(value):
    """Add form-control class to forms"""
    return mark_safe(re.sub(r'(type="(text|email|password)")', r'\1 class="form-control"', value))