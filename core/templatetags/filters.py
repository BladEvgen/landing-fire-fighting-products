from django import template

register = template.Library()


@register.filter(name="custom_cut")
def custom_cut(text, length):
    if len(str(text)) > length:
        return str(text)[:length] + "..."
    return str(text)


@register.filter
def chunked(lst, chunk_size):
    chunk_size = int(chunk_size)
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]
        
@register.filter
def split_once(value, arg=":"):
    if value and arg in value:
        return value.split(arg, 1)
    return [value, ""]

@register.filter
def strip(value):
    if value is not None:
        return str(value).strip()
    return value