from django.db import models
from django.urls import reverse
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete, pre_save, post_save
from django.core.validators import FileExtensionValidator, RegexValidator
from core.utils import (
    product_upload_path,
    katalog_upload_path,
    category_upload_path,
    product_image_upload_path,
    certificate_file_upload_path,
    certificate_image_upload_path,
)
from django.utils.text import slugify
from django.core.files.storage import default_storage


ALLOWED_IMAGE_EXTENSIONS = ["png", "jpeg", "webp", "jpg"]


class CompanyInfo(models.Model):
    name = models.CharField("Название компании", max_length=100, default="Вымпел-45")
    full_name = models.CharField(
        "Полное наименование", max_length=200, default="ООО «Вымпел-45»"
    )
    description = models.TextField(
        "Описание компании",
        default="Более 25 лет производим высококачественные металлокорпусные изделия пожарно-технического назначения.",
    )

    phone_regex = RegexValidator(
        regex=r"^\+?1?\d{9,15}$", message="Формат: '+999999999'. До 15 цифр."
    )
    phone = models.CharField(
        "Телефон",
        max_length=20,
        blank=True,
        help_text="Введите телефон в любом удобном формате: 8800004540, +7-800-000-4540, +7 800 000 4540 и т.д. Система автоматически отформатирует номер для отображения.",
    )
    email = models.EmailField("Email", blank=True)
    address = models.CharField("Адрес", max_length=200, blank=True)
    longtitude = models.FloatField(
        "Долгота",
        null=True,
        blank=True,
        help_text="Используется для отображения на карте",
    )
    latitude = models.FloatField(
        "Широта",
        null=True,
        blank=True,
        help_text="Используется для отображения на карте",
    )
    working_hours = models.CharField(
        "Часы работы", max_length=100, default="Пн-Пт: 8:00 - 18:00, Сб-Вс: выходной"
    )

    inn = models.CharField("ИНН", max_length=12, blank=True)
    kpp = models.CharField("КПП", max_length=9, blank=True)
    ogrn = models.CharField("ОГРН", max_length=15, blank=True)
    bank_details = models.TextField("Банковские реквизиты", blank=True)

    meta_description = models.TextField(
        "Описание для поисковиков", max_length=160, blank=True
    )
    meta_keywords = models.TextField("Ключевые слова", blank=True)

    hero_title = models.TextField(
        "Заголовок Hero-секции",
        blank=True,
        help_text="Большой заголовок на главной странице<br>HTML разрешен. Если пусто, используется стандартный заголовок",
    )
    hero_description = models.TextField("Описание под заголовком", blank=True)
    hero_image = models.ImageField("Фоновое изображение", upload_to="hero/", blank=True)

    cta_title = models.CharField(
        "Заголовок призыва к действию", max_length=200, blank=True
    )
    cta_description = models.TextField("Описание призыва к действию", blank=True)

    founded_year = models.PositiveIntegerField("Год основания", default=1999)
    experience_years = models.PositiveIntegerField("Лет опыта", default=25)

    requisites_file = models.FileField(
        "Файл реквизитов", upload_to="documents/", blank=True
    )
    price_list = models.FileField("Прайс-лист", upload_to="documents/", blank=True)

    vk_url = models.URLField("ВКонтакте", blank=True)
    telegram_url = models.URLField("Telegram", blank=True)
    whatsapp_phone = models.CharField("WhatsApp", max_length=17, blank=True)

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    statistics_html = models.TextField(
        "Код статистики",
        blank=True,
        help_text="""
        Здесь можно разместить HTML код для блока статистики на главной странице.
        Пример:
        <div class="stat-item">
            <span class="number">25+</span>
            <span class="text">лет опыта</span>
        </div>
        """,
    )

    requisites_file = models.FileField(
        "Файл реквизитов",
        upload_to="documents/",
        blank=True,
        help_text="PDF файл с реквизитами компании",
    )
    price_list = models.FileField(
        "Прайс-лист",
        upload_to="documents/",
        blank=True,
        help_text="Актуальный прайс-лист",
    )

    katalog = models.FileField(
        "Каталог продукции (PDF)",
        upload_to=katalog_upload_path,
        blank=True,
        help_text="Загрузите PDF каталог. Файл автоматически сохранится как katalog-vympel.pdf",
    )

    class Meta:
        verbose_name = "Информация о компании"
        verbose_name_plural = "Информация о компании"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.katalog and self.pk:
            try:
                old_instance = CompanyInfo.objects.get(pk=self.pk)
                if old_instance.katalog and old_instance.katalog != self.katalog:
                    if default_storage.exists("static/katalog-vympel.pdf"):
                        default_storage.delete("static/katalog-vympel.pdf")
            except CompanyInfo.DoesNotExist:
                pass

        super().save(*args, **kwargs)


class Certificate(models.Model):
    name = models.CharField("Название", max_length=200, help_text="Полное название сертификата или документа, лимит в 200 символов")
    description = models.TextField("Описание", blank=True, help_text="Дополнительная информация о сертификате")
    image = models.ImageField(
        "Изображение сертификата",
        upload_to=certificate_image_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_IMAGE_EXTENSIONS)
        ],
        help_text="Скан или фото сертификата для показа на сайте"
    )
    file = models.FileField("Файл сертификата",  upload_to=certificate_file_upload_path, blank=True)

    issued_date = models.DateField("Дата выдачи", null=True, blank=True)
    expiry_date = models.DateField("Дата окончания", null=True, blank=True, help_text="Оставьте пустым если сертификат бессрочный")

    is_active = models.BooleanField("Активен", default=True)
    sort_order = models.PositiveIntegerField("Порядок сортировки", default=0)

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"
        ordering = ["sort_order", "-issued_date"]

    def __str__(self):
        return self.name

    @property
    def is_expired(self):
        if self.expiry_date:
            from django.utils import timezone

            return timezone.now().date() > self.expiry_date
        return False

    @property
    def status_display(self):
        if self.is_expired:
            return "Истёк"
        elif self.expiry_date:
            return "Действителен"
        else:
            return "Бессрочный"

class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("URL", unique=True, blank=True)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField(
        "Изображение",
        upload_to=category_upload_path,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_IMAGE_EXTENSIONS)
        ],
    )
    icon = models.CharField("CSS класс иконки", max_length=50, blank=True,
                          help_text="Например: fa-fire для иконки огня, используйте Font Awesome FREE v.6 классы")
    meta_title = models.CharField("Meta Title", max_length=60, blank=True)
    meta_description = models.CharField("Meta Description", max_length=160, blank=True)

    is_active = models.BooleanField("Активна", default=True)
    sort_order = models.PositiveIntegerField("Порядок сортировки", default=0)

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:category_detail", args=[self.slug])

    @property
    def product_count(self):
        return self.product_set.filter(is_active=True).count()

class Tag(models.Model):
    name = models.CharField("Название тега", max_length=50,
                          help_text="Короткое название тега (например: Новинка)")
    slug = models.SlugField("URL", unique=True, blank=True)
    color = models.CharField(
        "Цвет",
        max_length=7,
        default="#ff6b00",
        help_text="HEX цвет для отображения тега",
    )

    is_active = models.BooleanField("Активен", default=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    name = models.CharField("Название товара", max_length=200,
                          help_text="Полное название товара")
    slug = models.SlugField("URL адрес", unique=True, blank=True)
    short_description = models.CharField("Краткое описание", max_length=300, blank=True,
                                       help_text="Краткое описание для карточки товара")
    description = models.TextField("Полное описание", blank=True,
                                 help_text="Подробное описание товара")
    image = models.ImageField(
        "Основное изображение",
        upload_to=product_upload_path,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_IMAGE_EXTENSIONS)
        ],
    )

    specifications = models.TextField(
        "Технические характеристики",
        blank=True,
        help_text="Каждую характеристику указывайте с новой строки в формате: <b>Название характеристики: Значение.</b> <br>Например:<br>Предел огнестойкости: не менее 60 мин.<br>Масса двери в сборе: не более 120 кг",
    )

    categories = models.ManyToManyField(Category, verbose_name="Категории", blank=True,
                                      help_text="Выберите одну или несколько категорий")
    tags = models.ManyToManyField(Tag, verbose_name="Теги", blank=True,
                                help_text="Теги для дополнительной фильтрации")

    is_active = models.BooleanField("Активен", default=True)
    is_featured = models.BooleanField(
        "Рекомендуемый",
        default=False,
        help_text="Отображается в разделе рекомендуемых товаров",
    )
    is_new = models.BooleanField("Новинка", default=False,
                               help_text="Будет отмечен как новинка")
    in_stock = models.BooleanField(
        "В наличии",
        default=True,
        help_text="Если нет в наличии, показывается 'Под заказ'",
    )

    sort_order = models.PositiveIntegerField(
        "Порядок сортировки", default=0, help_text="Чем меньше число, тем выше в списке"
    )

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("core:product_detail", args=[self.slug])

    @property
    def get_main_category(self):
        return self.categories.first()

    @property
    def get_specifications_dict(self):
        if not self.specifications:
            return {}

        specs = {}
        for line in self.specifications.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                specs[key.strip()] = value.strip()
        return specs

    @property
    def display_price(self):
        if self.price:
            prefix = "от " if self.price_from else ""
            return f"{prefix}{self.price:,.0f} ₽"
        return "Цена по запросу"


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="Товар"
    )
    image = models.ImageField(
        "Изображение",
        upload_to=product_image_upload_path,
        validators=[
            FileExtensionValidator(allowed_extensions=ALLOWED_IMAGE_EXTENSIONS)
        ],
        help_text="Дополнительные фотографии товара"
    )
    alt_text = models.CharField("Описание изображения", max_length=200, blank=True, help_text="Если картинка не загрузится, будет показан этот текст, также для доступности")
    sort_order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ["sort_order"]

    def __str__(self):
        return f"{self.product.name} - Изображение {self.sort_order}"


class ContactForm(models.Model):
    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email", blank=True)
    message = models.TextField("Сообщение", blank=True)

    ip_address = models.GenericIPAddressField("IP адрес", null=True, blank=True)
    user_agent = models.TextField("User Agent", blank=True)
    referer = models.URLField("Откуда пришел", blank=True)
    personal_data_consent = models.BooleanField(
        "Согласие на обработку персональных данных",
        default=False,
        help_text="Пользователь должен дать согласие на обработку персональных данных",
    )

    STATUS_CHOICES = [
        ("new", "Новая"),
        ("in_progress", "В работе"),
        ("completed", "Выполнена"),
        ("cancelled", "Отменена"),
    ]
    status = models.CharField(
        "Статус", max_length=20, choices=STATUS_CHOICES, default="new"
    )

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Заявка от {self.name} - {self.created_at.strftime('%d.%m.%Y %H:%M')}"


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField("Телефон", max_length=50, blank=True)

    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

    def __str__(self) -> str:
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    UserProfile.objects.get_or_create(user=instance)


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
