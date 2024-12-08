import os
from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import redirect, render, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseNotFound, JsonResponse, HttpResponse
from django.urls import reverse
from django.core import serializers

from library.forms import ShippingForm
from .models import (
    Book,
    Cart,
    CartItem,
    City,
    Order,
    OrderItem,
    Region,
    ShippingAddress,
    Upazila,
)
from django.views.generic import ListView, DetailView
from django.db.models import Sum, F
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
import requests
from dotenv import load_dotenv

load_dotenv()


class BookListView(ListView):
    model = Book
    # queryset = Book.objects.select_related("publication").select_related("category")
    paginate_by = 50
    context_object_name = "books"
    template_name = "library/books.html"

    def get_queryset(self) -> QuerySet[Any]:
        query = self.request.GET.get("search")
        if query:
            return (
                Book.objects.filter(title__icontains=query.lower())
                .select_related("publication")
                .select_related("category")
            )
        return Book.objects.select_related("publication").select_related("category")


# def home(request):
#     return render(request, "library/books.html")


# class BookDetailView(DetailView):

def book_detail(request, id):
    book = Book.objects.get(pk=id)
    if request.method == "POST":
        user = request.user
        # if not user.is_authenticated:
        #     return redirect(reverse('login'))
        cart, created = Cart.objects.get_or_create(user=user)
        try:
            cart_item = CartItem.objects.get(cart=cart, book_id=id)
            cart_item.quantity += 1
            cart_item.save()
            messages.success(request, "Book has added to cart")
        except CartItem.DoesNotExist:
            CartItem.objects.create(cart=cart, book_id=id, quantity=1)
            messages.success(request, "Book has added to cart")
        return render(request, "library/partials/cart-success.html")
    return render(request, "library/book-detail.html", {"book": book})


@login_required(login_url="/users/login/")
def cart_view(request):
    user = request.user.id
    cart, created = Cart.objects.get_or_create(user_id=user)
    cart_items = CartItem.objects.filter(cart=cart).annotate(
        total_price=F("quantity") * F("book__price")
    )

    total = cart_items.aggregate(total=Sum("total_price"))

    # books = Book.objects.filter(id__in=books_id)
    # print()
    return render(
        request, "library/cart.html", {"cart_items": cart_items, "total": total}
    )


@login_required(login_url="/users/login/")
def add_to_cart(request):
    if request.method == "POST":
        book_id = request.POST.get("book_id")
        quantity = request.POST.get("quantity", 1)
        cart, created = Cart.objects.get_or_create(user=request.user)
        try:
            cart_item = CartItem.objects.get(cart=cart, book_id=book_id)
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, "Book has added to cart")
        except CartItem.DoesNotExist:
            CartItem.objects.create(cart=cart, book_id=book_id, quantity=quantity)
            messages.success(request, "Book has added to cart")
        return HttpResponseRedirect(reverse("book-detail", kwargs={"id": book_id}))
    return HttpResponseNotFound()


@login_required(login_url="/users/login/")
def edit_cart_item(request):
    cart_item_id = request.POST.get("cart_item_id")
    item = CartItem.objects.get(pk=cart_item_id)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "INCREMENT":
            item.quantity += 1
            item.save()
        elif action == "DECREMENT":
            item.quantity -= 1
            item.save()
        elif action == "DELETE":
            item.delete()
        return JsonResponse({"success": True})


# def edit_cart_item(request, id):
#     cart_item = CartItem.objects.get(id=id)

#     return


def order_view(request):
    user = request.user
    orders = Order.objects.filter(user_id=user)
    # cart_items = CartItem.objects.filter(cart=cart).annotate(
    #     total_price=F("quantity") * F("book__price")
    # )
    return render(request, "library/orders.html", {"orders": orders})


@login_required(login_url="/users/login/")
def checkout(request):
    user = request.user
    cart, created = Cart.objects.get_or_create(user=user)
    items = CartItem.objects.filter(cart=cart).annotate(
        total_price=F("quantity") * F("book__price")
    )
    # order_items = OrderItem.objects.filter(order_id=id)
    total = items.aggregate(total=Sum("total_price"))
    addresses = ShippingAddress.objects.filter(user=user)

    if request.method == "POST":
        shipping_id = request.POST.get("shipping_id")
        order = Order.objects.create(
            shipping_address_id=shipping_id, user=request.user, total=total.get("total")
        )
        order_items = []
        for item in items:
            order_items.append(
                OrderItem(
                    order=order,
                    book=item.book,
                    quantity=item.quantity,
                    unit_price=item.book.price,
                )
            )
        OrderItem.objects.bulk_create(order_items)
        cart.delete()
        data = {
            "store_id": os.environ["STORE_ID"],
            "store_passwd": os.environ["STORE_PASSWD"],
            "total_amount": order.total,
            "currency": "BDT",
            "tran_id": str(order.id),
            "success_url": "http://127.0.0.1:8000/success/",
            "fail_url": "http://127.0.0.1:8000/fail/",
            "cancel_url": "http://127.0.0.1:8000/cancel/",
            "ipn_url": "http://127.0.0.1:8000/ipn/",
            "shipping_method": "Courier",
            "product_name": order.get_products(),
            "product_category": "Book",
            "product_profile": "general",
            "cus_name": order.shipping_address.name,
            "cus_email": order.user.email,
            "cus_add1": order.shipping_address.address,
            "cus_city": order.shipping_address.city.name,
            "cus_state": order.shipping_address.region.name,
            "cus_postcode": order.shipping_address.post_code,
            "cus_country": "Bangladesh",
            "cus_phone": order.shipping_address.phone,
            "ship_name": order.shipping_address.name,
            "ship_add1": order.shipping_address.address,
            "ship_city": order.shipping_address.city.name,
            "ship_state": order.shipping_address.region.name,
            "ship_postcode": order.shipping_address.post_code,
            "ship_country": "Bangladesh",
        }
        url = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"
        try:
            res = requests.post(url, data=data).json()
            return HttpResponseRedirect(res["GatewayPageURL"])
        except:
            pass

        # cart.delete()

    return render(
        request,
        "library/shipping.html",
        {"order_items": items, "total": total.get("total"), "addresses": addresses},
    )


def order_details(request, id):
    order = Order.objects.get(pk=id)
    total = OrderItem.objects.filter(order=order).aggregate(
        sub_total=Sum(F("quantity") * F("unit_price"))
    )
    return render(
        request, "library/order-details.html", {"order": order, "total": total}
    )


# def create_order(request):
#     user = request.user
#     cart = Cart.objects.get(user=user)
#     cart_items = CartItem.objects.filter(cart=cart).select_related("book")

#     if request.method == "POST":
#         with transaction.atomic():
#             order = Order.objects.create(user=user)
#             for item in cart_items:
#                 OrderItem.objects.create(
#                     order=order,
#                     book=item.book,
#                     quantity=item.quantity,
#                     unit_price=item.book.price,
#                 )
#             cart.delete()
#         return HttpResponseRedirect(reverse("order-details", args=[str(order.id)]))
#     return


# class CityListView(ListView):
#     model = Region
#     # template_name = "library/partials/cities.html"
#     context_object_name = "cities"
#     response_class = JsonResponse


def cities(request):
    region_id = request.GET.get("region")
    response = {}
    if region_id:
        cities = City.objects.filter(region_id=region_id).values("id", "name")
        return JsonResponse(list(cities), safe=False)
    cities = City.objects.values("id", "name")
    # response = serializers.serialize("json", cities)
    return JsonResponse(list(cities), safe=False)


def upazilas(request):
    city_id = request.GET.get("city")
    if city_id:
        cities = Upazila.objects.filter(city_id=city_id).values("id", "name")
        return JsonResponse(list(cities), safe=False)
    cities = City.objects.values("id", "name")
    # response = serializers.serialize("json", cities)
    return JsonResponse(list(cities), safe=False)


def create_shipping(request):
    form = ShippingForm()
    addresses = ShippingAddress.objects.filter(user=request.user)
    if request.method == "POST":
        form = ShippingForm(request.POST)
        if form.is_valid():
            shipping = form.save(commit=False)
            shipping.user = request.user
            shipping.save()
            return render(
                request, "library/partials/address-book.html", {"addresses": addresses}
            )
        else:
            return render(request, "library/partials/address-form.html", {"form": form})
    return render(request, "library/partials/address-form.html", {"form": form})


@csrf_exempt
def success_transaction(request):
    if request.method == "POST":
        val_id = request.POST["val_id"]
        tran_id = request.POST["tran_id"]
        validation_url = (
            "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php"
        )
        params = {
            "val_id": val_id,
            "store_id": os.environ["STORE_ID"],
            "store_passwd": os.environ["STORE_PASSWD"],
        }
        res = requests.get(validation_url, params=params).json()
        print(res)
        if res["status"] == "VALID" or res['status'] == 'VALIDATED':
            # update order
            order = Order.objects.get(pk=tran_id)
            order.status = "PAID"
            order.save()
            return HttpResponseRedirect(reverse("home"))
        else:
            return HttpResponse("transaction failed")
    return HttpResponse("Hello")
