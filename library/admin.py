from django.contrib import admin
from .models import (
    Author,
    Book,
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    Publication,
)
from django.contrib.admin import TabularInline


# admin.site.register(Category)
admin.site.register(Publication)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)


class AuthorInline(TabularInline):
    model = Book.author.through
    min_num = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ["title", "price", "inventory", "pages"]
    search_fields = ["title"]
    # inlines = [AuthorInline]


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(Category)
class CateogryAdmin(admin.ModelAdmin):
    search_fields = ["title"]
