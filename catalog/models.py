from django.db import models
from django.contrib.auth.models import User


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Страна')

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'

    def __str__(self):
        return self.name


class Brand(models.Model):
    name = models.CharField(max_length=100, verbose_name='Бренд')
    country = models.ForeignKey(
        Country,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='brands',
        verbose_name='Страна'
    )

    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(max_length=100, unique=True, verbose_name='Slug')

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Snowboard(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    length = models.PositiveIntegerField(verbose_name='Длина (см)')
    min_weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Мин. вес (кг)')
    max_weight = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Макс. вес (кг)')
    brand = models.ForeignKey(
        Brand,
        on_delete=models.CASCADE,
        related_name='snowboards',
        verbose_name='Бренд'
    )
    categories = models.ManyToManyField(
        Category,
        through='SnowboardCategory',
        related_name='snowboards',
        verbose_name='Категории'
    )
    FLEX_CHOICES = [
        ('camber', 'Кэмбер'),
        ('rocker', 'Рокер'),
        ('flat', 'Флэт'),
        ('hybrid', 'Гибрид'),
    ]
    flex = models.CharField(max_length=10, choices=FLEX_CHOICES, null=True, blank=True, verbose_name='Прогиб')
    stiffness = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Жёсткость (1-10)')
    image = models.ImageField(upload_to='snowboards/', null=True, blank=True, verbose_name='Фото')

    class Meta:
        verbose_name = 'Сноуборд'
        verbose_name_plural = 'Сноуборды'

    def __str__(self):
        return f'{self.brand} — {self.name} ({self.length} см)'


class SnowboardCategory(models.Model):
    snowboard = models.ForeignKey(Snowboard, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('snowboard', 'category')
        verbose_name = 'Категория сноуборда'
        verbose_name_plural = 'Категории сноубордов'

    def __str__(self):
        return f'{self.snowboard} / {self.category}'


class Resort(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    map = models.CharField(max_length=255, verbose_name='Ссылка на карту')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Широта')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='Долгота')
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Страна')
    image = models.ImageField(upload_to='resorts/', null=True, blank=True, verbose_name='Фото')
    resort_map = models.ImageField(upload_to='resort_maps/', null=True, blank=True, verbose_name='Карта трасс')

    class Meta:
        verbose_name = 'Курорт'
        verbose_name_plural = 'Курорты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    snowboard = models.ForeignKey(
        Snowboard,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Сноуборд'
    )

    class Meta:
        unique_together = ('user', 'snowboard')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return f'{self.user.username} → {self.snowboard}'


class SelectionHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    snowboard = models.ForeignKey(Snowboard, on_delete=models.CASCADE)
    rider_weight = models.PositiveIntegerField()
    rider_height = models.PositiveIntegerField()
    riding_style = models.CharField(max_length=50)
    compatibility = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name='Рост (см)')
    weight = models.PositiveIntegerField(null=True, blank=True, verbose_name='Вес (кг)')