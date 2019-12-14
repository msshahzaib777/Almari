from django import  template

register = template.Library()

from..models import product

@register.filter
def index(List, i):
    return List[int(i)]

@register.filter
def lenth(List):
    return len(List)    