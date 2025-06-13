
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Создает группы пользователей с правами доступа'

    def handle(self, *args, **options):
        content_managers, created = Group.objects.get_or_create(name="Контент-менеджеры")
        
        if created:
            self.stdout.write('Создана группа "Контент-менеджеры"')
        
        models_permissions = [
            ("change_companyinfo", "core", "companyinfo"),
            ("change_product", "core", "product"),
            ("add_product", "core", "product"),
            ("change_productimage", "core", "productimage"),
            ("add_productimage", "core", "productimage"),
            ("delete_productimage", "core", "productimage"),
            ("change_category", "core", "category"),
            ("add_category", "core", "category"),
            ("change_tag", "core", "tag"),
            ("add_tag", "core", "tag"),
            ("change_certificate", "core", "certificate"),
            ("add_certificate", "core", "certificate"),
            ("change_contactform", "core", "contactform"),
        ]

        added_permissions = 0
        for codename, app_label, model in models_permissions:
            try:
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                permission = Permission.objects.get(
                    content_type=content_type, codename=codename
                )
                content_managers.permissions.add(permission)
                added_permissions += 1
            except (ContentType.DoesNotExist, Permission.DoesNotExist):
                self.stdout.write(
                    self.style.WARNING(f'Разрешение {codename} для {app_label}.{model} не найдено')
                )

        self.stdout.write(f'Добавлено {added_permissions} разрешений для контент-менеджеров')

        contact_managers, created = Group.objects.get_or_create(name="Менеджеры заявок")
        
        if created:
            self.stdout.write('Создана группа "Менеджеры заявок"')
        
        contact_permissions = [
            ("change_contactform", "core", "contactform"),
            ("view_contactform", "core", "contactform"),
        ]

        added_contact_permissions = 0
        for codename, app_label, model in contact_permissions:
            try:
                content_type = ContentType.objects.get(app_label=app_label, model=model)
                permission = Permission.objects.get(
                    content_type=content_type, codename=codename
                )
                contact_managers.permissions.add(permission)
                added_contact_permissions += 1
            except (ContentType.DoesNotExist, Permission.DoesNotExist):
                self.stdout.write(
                    self.style.WARNING(f'Разрешение {codename} для {app_label}.{model} не найдено')
                )

        self.stdout.write(f'Добавлено {added_contact_permissions} разрешений для менеджеров заявок')
        
        self.stdout.write(
            self.style.SUCCESS('Группы пользователей успешно настроены!')
        )