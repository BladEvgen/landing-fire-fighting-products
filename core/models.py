from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.core.validators import FileExtensionValidator
from django.db.models.signals import post_delete, pre_save


ALLOWED_IMAGE_EXTENSIONS = ["png", "jpeg", "webp", "jpg"]


class CompanyInfo(models.Model):
    name = models.CharField("Название компании", max_length=255)
    legal_address = models.CharField("Юридический адрес", max_length=500)
    phone = models.CharField("Телефон", max_length=50)
    email = models.EmailField("Email")
    about = models.TextField("Описание", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Информация о компании"
        verbose_name_plural = "Информация о компании"

    def __str__(self) -> str:
        return self.name


class Certificate(models.Model):
    title = models.CharField("Название", max_length=255)
    image = models.ImageField(
        "Изображение",
        upload_to="certificates/",
        validators=[FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"

    def __str__(self) -> str:
        return self.title


class Category(models.Model):
    name = models.CharField("Название", max_length=255)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    title = models.CharField("Название", max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField(
        "Изображение",
        upload_to="products/",
        validators=[FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS)],
    )
    categories = models.ManyToManyField(Category, verbose_name="Категории", blank=True)
    tags = models.ManyToManyField(Tag, verbose_name="Теги", blank=True)
    price = models.DecimalField(
        "Цена", max_digits=10, decimal_places=2, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(
        "Изображение",
        upload_to="products/gallery/",
        validators=[FileExtensionValidator(ALLOWED_IMAGE_EXTENSIONS)],
    )

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товара"

    def __str__(self) -> str:
        return f"Image for {self.product.title}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField("Телефон", max_length=50, blank=True)

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self) -> str:
        return self.user.username


class PasswordResetTokenManager(models.Manager):
    def mark_as_used(self, token):
        token_obj = self.filter(token=token, _used=False).first()
        if token_obj and token_obj.is_valid():
            token_obj._used = True
            token_obj.save(update_fields=["_used"])
            return True
        return False


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    token = models.CharField(max_length=64, unique=True, verbose_name="Токен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    _used = models.BooleanField(default=False, verbose_name="Статус использования")

    objects = PasswordResetTokenManager()

    @property
    def used(self):
        return self._used

    def is_valid(self):
        expiration_time = timezone.now() - timezone.timedelta(hours=1)
        return self.created_at > expiration_time and not self._used

    @staticmethod
    def generate_token(user):
        from django.utils.crypto import get_random_string

        token = get_random_string(64)
        PasswordResetToken.objects.create(user=user, token=token)
        return token

    def save(self, *args, **kwargs):
        if self.pk:
            original = PasswordResetToken.objects.get(pk=self.pk)
            if original.token != self.token:
                self.token = original.token
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Токен для сброса пароля"
        verbose_name_plural = "Токены для сброса паролей"


class PasswordResetRequestLog(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name="Пользователь"
    )
    ip_address = models.GenericIPAddressField(verbose_name="IP-адрес")
    requested_at = models.DateTimeField(auto_now_add=True, verbose_name="Время запроса")

    @staticmethod
    def is_recent_request(user, ip_address):
        five_minutes_ago = timezone.now() - timezone.timedelta(minutes=5)
        return PasswordResetRequestLog.objects.filter(
            user=user, ip_address=ip_address, requested_at__gte=five_minutes_ago
        ).exists()

    @staticmethod
    def get_last_request_time(user, ip_address):
        last_request = (
            PasswordResetRequestLog.objects.filter(user=user, ip_address=ip_address)
            .order_by("-requested_at")
            .first()
        )
        return last_request.requested_at if last_request else None

    @staticmethod
    def log_request(user, ip_address):
        PasswordResetRequestLog.objects.create(user=user, ip_address=ip_address)

    @staticmethod
    def can_request_again(user, ip_address):
        last_request_time = PasswordResetRequestLog.get_last_request_time(
            user, ip_address
        )
        if not last_request_time:
            return True
        return timezone.now() >= last_request_time + timezone.timedelta(minutes=5)

    class Meta:
        verbose_name = "Лог запросов на сброс пароля"
        verbose_name_plural = "Логи запросов на сброс пароля"


@receiver(post_delete, sender=Certificate)
@receiver(post_delete, sender=ProductImage)
@receiver(post_delete, sender=Product)
def delete_file_on_delete(sender, instance, **kwargs):
    file_field = getattr(instance, "image", None)
    if file_field and file_field.name:
        file_field.storage.delete(file_field.name)


@receiver(pre_save, sender=Certificate)
@receiver(pre_save, sender=Product)
@receiver(pre_save, sender=ProductImage)
def validate_image_extension(sender, instance, **kwargs):
    file_field = getattr(instance, "image", None)
    if file_field and file_field.name:
        ext = file_field.name.split(".")[-1].lower()
        if ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationError(
                f"Недопустимый формат файла: {ext}. Допустимы {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
            )
