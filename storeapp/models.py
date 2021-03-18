import sys
from PIL import Image

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.urls import reverse
from io import BytesIO
from autoslug import AutoSlugField

User = get_user_model()


def get_product_url(obj, viewname):
    ct_model = obj.__class__._meta.model_name
    return reverse(viewname, kwargs={
                                    'ct_model': ct_model,
                                    'slug': obj.slug,
                                })


class MinResolutionImageException(Exception):
    pass

class MaxResolutionImageException(Exception):
    pass

class MaxImageSizeException(Exception):
    pass

class Category(models.Model):

    name = models.CharField('Имя категории', max_length=255)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Product(models.Model):

    MIN_RESOLUTION = (400, 400)
    MAX_RESOLUTION = (900, 900)
    MAX_IMAGE_SIZE = 3145728

    class Meta:
        abstract = True

    category = models.ForeignKey(Category, verbose_name='Категория', on_delete=models.CASCADE)
    title = models.CharField('Наименование', max_length=255)
    slug = models.SlugField(unique=True)
    image = models.ImageField('Изображение')
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField('Цена', max_digits=9, decimal_places=2)

    def save(self, *args, **kwargs):

        image = self.image
        img = Image.open(image)
        max_height, max_width = self.MAX_RESOLUTION
        if image.size > self.MAX_IMAGE_SIZE:
            raise MaxImageSizeException('Размер изображения не должен привышать 3МБ')
        if img.height > max_height or img.width > max_width:
            new_img = img.convert('RGB')
            resized_new_img = new_img.resize((400, 400), Image.ANTIALIAS)
            filestream = BytesIO()
            resized_new_img.save(filestream, 'JPEG', quality=90)
            file_.seek(0)
            name = '{}.{}'.format(*self.image.name.split('.'))
            self.image = (
                filestream, 'ImageField', name, 'jpeg/image', sys.getsizeof(file_), None
            )

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Noteboocks(Product):

    diagonal = models.CharField('Диагональ', max_length=255)
    display_type = models.CharField('Тип дисплея', max_length=255)
    processor_freq = models.CharField('Частота процессора', max_length=255)
    ram = models.CharField('Оперативная память', max_length=255)
    video = models.CharField('Видеокарта', max_length=255)
    time_without_charge = models.CharField('Время работы аккумулятора', max_length=255)

    def __str__(self):
        return '{} | {}'.format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class Smartphones(Product):

    SMARTPHONES_STATS = {
        'MAX_MEMORY_VALUE_CHOICE': (
                ('1 GB', '1 gb'),
                ('2 GB', '2 gb'),
                ('4 GB', '4 gb'),
                ('8 GB', '8 gb'),
                ('16 GB', '16 gb'),
                ('32 GB', '32 gb'),
                ('64 GB', '64 gb'),
                ('128 GB', '128 gb'),
                ('256 GB', '256 gb'),
                ('512 GB', '512 gb'),
            ),

        'RAM_MEMORY_VALUE_CHOICE': (
                ('1 GB', '1 gb'),
                ('2 GB', '2 gb'),
                ('4 GB', '4 gb'),
                ('6 GB', '6 gb'),
                ('8 GB', '8 gb'),
                ('12 GB', '12 gb'),
                ('16 GB', '16 gb'),
            ),

        'SMARTPHONE_SCREEN_RESOLUTIONS': (
            ('1280 х 720', '720p'),
            ('1920 x 1080', '1080p'),
            ('2560 x 1440', '2K'),
            ('3840 x 2160', '4К'),
        )
    }

    diagonal = models.CharField('Диагональ', max_length=255)
    display_type = models.CharField('Тип дисплея', max_length=255)
    resolution = models.CharField('Разрешение экрана', max_length=255,
                                  choices=SMARTPHONES_STATS['SMARTPHONE_SCREEN_RESOLUTIONS'], null=True, blank=True)
    unstandart_resolution = models.BooleanField('Нестандартное разрешение экрана', default=False)
    input_resolution = models.CharField('Другое разрешение экрана', max_length=255, null=True, blank=True)
    accum_value = models.CharField('Объем аккумулятора', max_length=255)
    ram = models.CharField('Оперативная память', max_length=255, choices=SMARTPHONES_STATS['RAM_MEMORY_VALUE_CHOICE'])
    sd = models.BooleanField('Наличие SD карты', default=True)
    sd_values_max = models.CharField('Максимальный объем sd карты', max_length=255, null=True, blank=True,
                                     choices=SMARTPHONES_STATS['MAX_MEMORY_VALUE_CHOICE'])
    frontal_cam_mp = models.CharField('Фронтальная камера (в мегапикселях)', max_length=255)
    main_cam_mp = models.CharField('Основная камера (в мегапикселях)', max_length=255)

    def __str__(self):
        return '{} | {}'.format(self.category.name, self.title)

    def get_absolute_url(self):
        return get_product_url(self, 'product_detail')


class CartProduct(models.Model):

    user = models.ForeignKey('Customer', verbose_name='Покупатель', on_delete=models.CASCADE)
    cart = models.ForeignKey('Cart', verbose_name='Корзина', on_delete=models.CASCADE, related_name='related_products')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    qrt = models.PositiveIntegerField('Количество', default=1)
    final_price = models.DecimalField('Финальная цена', max_digits=9, decimal_places=2)

    def __str__(self):
        return 'Cart product {}'.format(self.content_type.title)

class Cart(models.Model):

    owner = models.ForeignKey('Customer', verbose_name='Пользователь', on_delete=models.CASCADE)
    products = models.ManyToManyField(CartProduct, blank=True, related_name='related_cart')
    total_products = models.PositiveIntegerField('Количество продуктов', default=0)
    final_price = models.DecimalField('Финальная цена', max_digits=9, decimal_places=2)
    in_order = models.BooleanField(default=False)
    for_anonimous_user = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)


class Customer(models.Model):

    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    phone = models.CharField('Номер', max_length=20)
    address = models.CharField('Адрес', max_length=255)

    def __str__(self):
        return 'Customer: {} {}'.format(self.user.first_name, self.user.last_name)