import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


# Create your models here.
class Category(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.title


class Publication(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Author(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


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

    def __str__(self) -> str:
        return self.title


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
    ("PAID", "PAID"),
    ("CANCELED", "Canceled"),
    ("SHIPPED", "Shipped"),
)


class Region(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class City(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Upazila(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class ShippingAddress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    upazila = models.ForeignKey(Upazila, on_delete=models.CASCADE)
    address = models.CharField(max_length=512)
    post_code = models.CharField(max_length=10)
    phone = models.CharField(
        max_length=20,
        validators=[
            MinLengthValidator(11, message="Phone number must be 11 characters long.")
        ],
    )

    def __str__(self) -> str:
        return f"{self.address} -  {self.city}, {self.region}"


class Order(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default="PENDING", choices=ORDER_STATUS)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        ordering = ['-created_at']
    
    def get_products(self):
        items = self.orderitem_set.all()
        products = []
        for i in items:
            products.append(i.book.title)
        return ",".join(products)

class OrderItem(models.Model):
    book = models.ForeignKey(Book, on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
