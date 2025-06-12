from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.dispatch import receiver
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models.signals import post_delete, pre_save
from django.core.validators import FileExtensionValidator, RegexValidator

ALLOWED_IMAGE_EXTENSIONS = ["png", "jpeg", "webp", "jpg"]


class CompanyInfo(models.Model):
    """Модель для хранения информации о компании"""
    
    # Основная информация
    name = models.CharField("Название компании", max_length=100, default="Вымпел-45")
    full_name = models.CharField("Полное наименование", max_length=200, default="ООО «Вымпел-45»")
    description = models.TextField("Описание компании", 
                                  default="Более 25 лет производим высококачественные металлокорпусные изделия пожарно-технического назначения.")
    
    # Контактная информация
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$', message="Формат: '+999999999'. До 15 цифр.")
    phone = models.CharField("Телефон", validators=[phone_regex], max_length=17, blank=True)
    email = models.EmailField("Email", blank=True)
    address = models.CharField("Адрес", max_length=200, blank=True)
    working_hours = models.CharField("Часы работы", max_length=100, 
                                   default="Пн-Пт: 8:00 - 18:00, Сб-Вс: выходной")
    
    # Реквизиты
    inn = models.CharField("ИНН", max_length=12, blank=True)
    kpp = models.CharField("КПП", max_length=9, blank=True)
    ogrn = models.CharField("ОГРН", max_length=15, blank=True)
    bank_details = models.TextField("Банковские реквизиты", blank=True)
    
    # SEO и контент
    meta_description = models.TextField("Мета-описание", max_length=160, blank=True)
    meta_keywords = models.TextField("Ключевые слова", blank=True)
    
    # Hero секция
    hero_title = models.TextField("Заголовок Hero-секции", blank=True,
                                 help_text="HTML разрешен. Если пусто, используется стандартный заголовок")
    hero_description = models.TextField("Описание Hero-секции", blank=True)
    hero_image = models.ImageField("Изображение Hero-секции", upload_to='hero/', blank=True)
    
    # CTA секция
    cta_title = models.CharField("Заголовок призыва к действию", max_length=200, blank=True)
    cta_description = models.TextField("Описание призыва к действию", blank=True)
    
    # Дополнительная информация
    founded_year = models.PositiveIntegerField("Год основания", default=1999)
    experience_years = models.PositiveIntegerField("Лет опыта", default=25)
    
    # Файлы
    requisites_file = models.FileField("Файл реквизитов", upload_to='documents/', blank=True)
    price_list = models.FileField("Прайс-лист", upload_to='documents/', blank=True)
    
    # Социальные сети
    vk_url = models.URLField("ВКонтакте", blank=True)
    telegram_url = models.URLField("Telegram", blank=True)
    whatsapp_phone = models.CharField("WhatsApp", max_length=17, blank=True)
    
    # Системные поля
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)
    
    class Meta:
        verbose_name = "Информация о компании"
        verbose_name_plural = "Информация о компании"
    
    def __str__(self):
        return self.name


class Certificate(models.Model):
    """Сертификаты компании"""
    name = models.CharField("Название", max_length=200)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение сертификата", upload_to='certificates/')
    file = models.FileField("Файл сертификата", upload_to='certificates/', blank=True)
    
    # Даты действия
    issued_date = models.DateField("Дата выдачи", null=True, blank=True)
    expiry_date = models.DateField("Дата окончания", null=True, blank=True)
    
    # Настройки
    is_active = models.BooleanField("Активен", default=True)
    sort_order = models.PositiveIntegerField("Порядок сортировки", default=0)
    
    # Системные поля
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)
    
    class Meta:
        verbose_name = "Сертификат"
        verbose_name_plural = "Сертификаты"
        ordering = ['sort_order', '-issued_date']
    
    def __str__(self):
        return self.name
    
    @property
    def is_expired(self):
        """Проверка истечения срока действия"""
        if self.expiry_date:
            from django.utils import timezone
            return timezone.now().date() > self.expiry_date
        return False


class Category(models.Model):
    """Категории товаров"""
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField("URL", unique=True, blank=True)
    description = models.TextField("Описание", blank=True)
    image = models.ImageField("Изображение", upload_to='categories/', blank=True)
    icon = models.CharField("Иконка (CSS класс)", max_length=50, blank=True)
    
    # SEO
    meta_title = models.CharField("Meta Title", max_length=60, blank=True)
    meta_description = models.CharField("Meta Description", max_length=160, blank=True)
    
    # Настройки
    is_active = models.BooleanField("Активна", default=True)
    sort_order = models.PositiveIntegerField("Порядок сортировки", default=0)
    
    # Системные поля
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('core:category_detail', args=[self.slug])

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
    """Теги для товаров"""
    name = models.CharField("Название", max_length=50)
    slug = models.SlugField("URL", unique=True, blank=True)
    color = models.CharField("Цвет", max_length=7, default="#ff6b00", 
                           help_text="HEX цвет для отображения тега")
    
    is_active = models.BooleanField("Активен", default=True)
    
    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Товары"""
    name = models.CharField("Название", max_length=200)
    slug = models.SlugField("URL", unique=True, blank=True)
    short_description = models.CharField("Краткое описание", max_length=300, blank=True)
    description = models.TextField("Полное описание", blank=True)
    
    # Изображения
    main_image = models.ImageField("Основное изображение", upload_to='products/', blank=True)
    
    # Цена и наличие
    price = models.DecimalField("Цена", max_digits=10, decimal_places=2, null=True, blank=True)
    price_from = models.BooleanField("Цена от", default=True)
    in_stock = models.BooleanField("В наличии", default=True)
    
    # Характеристики
    specifications = models.JSONField("Характеристики", default=dict, blank=True,
                                    help_text="JSON с характеристиками товара")
    
    # Связи
    categories = models.ManyToManyField(Category, verbose_name="Категории", blank=True)
    tags = models.ManyToManyField(Tag, verbose_name="Теги", blank=True)
    
    # SEO
    meta_title = models.CharField("Meta Title", max_length=60, blank=True)
    meta_description = models.CharField("Meta Description", max_length=160, blank=True)
    
    # Настройки
    is_active = models.BooleanField("Активен", default=True)
    is_featured = models.BooleanField("Рекомендуемый", default=False)
    is_new = models.BooleanField("Новинка", default=False)
    sort_order = models.PositiveIntegerField("Порядок сортировки", default=0)
    
    # Системные поля
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['sort_order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('core:product_detail', args=[self.slug])
    
    @property
    def display_price(self):
        """Форматированная цена для отображения"""
        if self.price:
            prefix = "от " if self.price_from else ""
            return f"{prefix}{self.price:,.0f} ₽"
        return "Цена по запросу"


class ProductImage(models.Model):
    """Дополнительные изображения товаров"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, 
                               related_name='images', verbose_name="Товар")
    image = models.ImageField("Изображение", upload_to='products/')
    alt_text = models.CharField("Alt текст", max_length=200, blank=True)
    sort_order = models.PositiveIntegerField("Порядок", default=0)
    
    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"
        ordering = ['sort_order']
    
    def __str__(self):
        return f"{self.product.name} - Изображение {self.sort_order}"

class ContactForm(models.Model):
    """Модель для заявок с сайта"""
    name = models.CharField("Имя", max_length=100)
    phone = models.CharField("Телефон", max_length=20)
    email = models.EmailField("Email", blank=True)
    message = models.TextField("Сообщение", blank=True)
    
    # Системная информация
    ip_address = models.GenericIPAddressField("IP адрес", null=True, blank=True)
    user_agent = models.TextField("User Agent", blank=True)
    referer = models.URLField("Откуда пришел", blank=True)
    
    # Статусы
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнена'),
        ('cancelled', 'Отменена'),
    ]
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='new')
    
    # Системные поля
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)
    
    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ['-created_at']
    
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
