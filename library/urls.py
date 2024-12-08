from django.urls import path
from . import views

urlpatterns = [
    path("", views.BookListView.as_view(), name="home"),
    path("cart/", views.cart_view, name="cart"),
    path("add-to-cart/", views.add_to_cart, name="add-to-cart"),
    path("books/<int:id>/", views.book_detail, name="book-detail"),
    path("edit-cart-item/", views.edit_cart_item, name="edit-cart-item"),
    path("orders/", views.order_view, name="orders"),
    path("orders/<str:id>/", views.order_details, name="order-details"),
    # path("create-order/", views.create_order, name="create-order"),
    path("checkout/", views.checkout, name="checkout"),
    path("create-shipping/", views.create_shipping, name="create-shipping"),
    path("cities/", views.cities, name="city-list"),
    path("upazilas/", views.upazilas, name="upazilas"),
    path("success/", views.success_transaction)
]
