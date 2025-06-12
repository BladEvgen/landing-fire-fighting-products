from django import template

register = template.Library()


@register.filter(name="custom_cut")
def custom_cut(text, length):
    if len(str(text)) > length:
        return str(text)[:length] + "..."
    return str(text)
