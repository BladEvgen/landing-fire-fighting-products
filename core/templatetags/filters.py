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