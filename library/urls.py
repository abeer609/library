from django.urls import path
from . import views

urlpatterns = [
    path("", views.BookListView.as_view(), name="home"),
    path("cart/", views.cart_view, name="cart"),
    path("add-to-cart/", views.add_to_cart, name="add-to-cart"),
    path("books/<int:id>/", views.book_detail, name="book-detail"),
    path("edit-cart-item/", views.edit_cart_item, name="edit-cart-item"),
    path("orders/", views.order_view, name="orders"),
]
