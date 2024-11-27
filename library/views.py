from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponseNotFound, JsonResponse
from django.urls import reverse
from .models import Book, Cart, CartItem, Order
from django.views.generic import ListView, DetailView
from django.db.models import Sum, F
from django.contrib import messages
from django.contrib.auth.decorators import login_required


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
    # book = {
    #     "title": "গাযযার সেই মেয়েটি",
    #     "description": "কুরআন-হাদিসের সাথে আমরা খুব একটা পরিচিত না। প্রয়োজনের তাগিদে কুরআন থেকে দু’একটা আয়াত তিলাওয়াত করি, বড়জোড় দু’একটা হাদিসের অনুবাদ পড়ি। গভীর ভাবে চিন্তা-ভাবনা করি না। জীবনকে ঢেলে সাজানোর জন্য মুক্তোর ন্যায় রত্নভাণ্ডার হলো, কুরআন ও হাদিস। বিস্ময়কর ওহি। যা জীবনের নব-জাগরণের রোডম্যাপ।মুক্তি লাভের মূলমন্ত্র। কুরআন-হাদিস অধ্যয়ন করে গল্পে গল্পে পাঠককে চিন্তার নতুন খোরাক দেয়ার চেষ্টা করেছি।পাঠক, মুক্তি লাভের মন্ত্র খোঁজে পাবে। ইনশাআল্লাহ।কুরআন-হাদিস কর্ষণ করেও যে গল্পে গল্পে জীবনের পাঠ শেখা যায়.. বইটি না পড়লে পাঠক বুঝতে পারবে না।অনেক স্বপ্ন থাকে জীবন নামের ভাবনার জগতে। স্বপ্নের বহি:প্রকাশ  প্রতিটি গল্পে পাঠক অনুধাবন করবে বলে আশাবাদি।",
    #     "image": "https://wafilife-media.wafilife.com/uploads/2019/09/ek-dighol-dine-nobiji-250x390.png",
    #     "pages": 128,
    #     "published_at": "2024-01-01",
    #     "category": "আত্মশুদ্ধি ও অনুপ্রেরণা",
    #     "publication": "মহিউদ্দিন বিন জুবায়েদ",
    #     "author": "শায়খ সালেহ আহমদ আশ-শামী",
    #     "inventory": 10,
    #     "price": "245",
    # }
    book = Book.objects.get(pk=id)
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
        return HttpResponseRedirect(reverse("home"))
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


def order_view(request):
    user = request.user
    orders = Order.objects.filter(user_id=user)
    # cart_items = CartItem.objects.filter(cart=cart).annotate(
    #     total_price=F("quantity") * F("book__price")
    # )
    return render(request, "library/orders.html", {"orders": orders})
