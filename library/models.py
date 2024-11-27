import uuid
from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=50)


class Publication(models.Model):
    name = models.CharField(max_length=100)


class Author(models.Model):
    name = models.CharField(max_length=100)


class Book(models.Model):
    title = models.CharField(max_length=512)
    description = models.TextField()
    cover_image = models.URLField()
    published_at = models.DateField(auto_now_add=True)
    author = models.ManyToManyField(Author, related_name="books")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE)
    inventory = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    pages = models.PositiveIntegerField()
    isbn = models.CharField(max_length=13, blank=True, null=True)


class Cart(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="carts")
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    book = models.ForeignKey(
        Book, on_delete=models.CASCADE, related_name="books_in_cart"
    )
    quantity = models.PositiveIntegerField()


ORDER_STATUS = (
    ("PENDING", "Pending"),
    ("CANCELED", "Canceled"),
    ("SHIPPED", "Shipped"),
)


class Order(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="PENDING", choices=ORDER_STATUS)


class OrderItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.DO_NOTHING)
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
