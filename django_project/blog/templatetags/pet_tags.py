from django import template
from django.utils.translation import gettext_lazy as _

register = template.Library()

@register.filter
def pet_age_label(age):
    if age < 1:
        return _("месяц")
    elif age == 1:
        return _("год")
    elif 2 <= age <= 4:
        return _("года")
    else:
        return _("лет")