import django_filters

from library.models import Book


class BookFilter(django_filters.FilterSet):
    class Meta:
        model = Book
        fields = ["name", "publication", "category"]
