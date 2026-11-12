from django.contrib import admin
from .models import Country, Brand, Category, Snowboard, SnowboardCategory, Resort, Favorite


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'country')
    list_filter = ('country',)
    search_fields = ('name',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class SnowboardCategoryInline(admin.TabularInline):
    model = SnowboardCategory
    extra = 1


@admin.register(Snowboard)
class SnowboardAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'brand', 'length', 'min_weight', 'max_weight')
    list_filter = ('brand', 'categories')
    search_fields = ('name', 'brand__name')
    inlines = [SnowboardCategoryInline]


@admin.register(Resort)
class ResortAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'snowboard')
    list_filter = ('user',)