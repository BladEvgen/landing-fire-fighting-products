from django.utils.text import slugify

def upload_to_slugified(
    instance,
    filename,
    prefix=None,
    name_field="name",
    related_object=None,
    numbered=False,
):
    ext = filename.split(".")[-1]
    if related_object:
        name = getattr(getattr(instance, related_object), name_field, None)
    else:
        name = getattr(instance, name_field, None)
    base = slugify(name) if name else "file"

    if numbered:
        number = getattr(instance, "sort_order", None) or getattr(instance, "pk", None)
        filename = f"{base}_{number}.{ext}" if number else f"{base}.{ext}"
    else:
        filename = f"{base}.{ext}"

    return f"{prefix}/{filename}"


def category_upload_path(instance, filename):
    return upload_to_slugified(instance, filename, prefix="categories")


def product_upload_path(instance, filename):
    return upload_to_slugified(instance, filename, prefix="products")


def product_image_upload_path(instance, filename):
    return upload_to_slugified(instance, filename, prefix="products")

def katalog_upload_path(instance, filename):
    return "static/katalog-vympel.pdf"

def certificate_image_upload_path(instance, filename):
    return upload_to_slugified(instance, filename, prefix="certificates/images")

def certificate_file_upload_path(instance, filename):
    return upload_to_slugified(instance, filename, prefix="certificates/files")