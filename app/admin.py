from django.contrib import admin
from .models import Author, Book, Work, BookAuthor


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'middle_name', 'birth_year', 'death_year']
    search_fields = ['last_name', 'first_name', 'middle_name']
    list_filter = ['birth_year']


# Inline для отображения авторов в админке книги
class BookAuthorInline(admin.TabularInline):
    model = BookAuthor
    extra = 1
    raw_id_fields = ['author']
    autocomplete_fields = ['author']


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'inventory_number', 'publisher', 'publication_year']
    search_fields = ['title', 'inventory_number', 'publisher']
    list_filter = ['publication_year']
    inlines = [BookAuthorInline]  # Используем inline вместо filter_horizontal
    fieldsets = (
        (None, {
            'fields': ('title', 'inventory_number', 'publisher', 'publication_year', 'pages', 'description',
                       'cover_image')
        }),
    )


@admin.register(Work)
class WorkAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'book', 'work_type', 'first_page', 'last_page']
    search_fields = ['title', 'author__last_name', 'author__first_name']
    list_filter = ['work_type', 'book', 'publication_year']
    autocomplete_fields = ['author', 'book']
    readonly_fields = ['page_range']

    def page_range(self, obj):
        return obj.page_range

    page_range.short_description = 'Диапазон страниц'


@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ['book', 'author', 'role']
    list_filter = ['role']
    search_fields = ['book__title', 'author__last_name', 'author__first_name']
    autocomplete_fields = ['book', 'author']