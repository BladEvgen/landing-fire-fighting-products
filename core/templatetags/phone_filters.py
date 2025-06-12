import re
from django import template

register = template.Library()


@register.filter
def format_phone(phone):
    """
    Обрабатывает различные форматы ввода:
    - 8800004540 -> +7 800 000-45-40
    - 7800004540 -> +7 800 000-45-40
    - +7800004540 -> +7 800 000-45-40
    - +7-800-000-4540 -> +7 800 000-45-40
    - +7 800 000 4540 -> +7 800 000-45-40
    """
    if not phone:
        return ""

    digits_only = re.sub(r"\D", "", phone)

    if digits_only.startswith("8") and len(digits_only) == 11:
        digits_only = "7" + digits_only[1:]

    if not digits_only.startswith("7"):
        digits_only = "7" + digits_only

    if len(digits_only) != 11:
        return phone

    formatted = f"+7 {digits_only[1:4]} {digits_only[4:7]}-{digits_only[7:9]}-{digits_only[9:11]}"

    return formatted


@register.filter
def format_phone_link(phone):
    if not phone:
        return ""

    digits_only = re.sub(r"\D", "", phone)

    if digits_only.startswith("8") and len(digits_only) == 11:
        digits_only = "7" + digits_only[1:]

    if not digits_only.startswith("7"):
        digits_only = "7" + digits_only

    return f"+{digits_only}"


@register.filter
def format_whatsapp_link(phone):
    if not phone:
        return ""

    digits_only = re.sub(r"\D", "", phone)

    if digits_only.startswith("8") and len(digits_only) == 11:
        digits_only = "7" + digits_only[1:]

    if not digits_only.startswith("7"):
        digits_only = "7" + digits_only

    return digits_only
