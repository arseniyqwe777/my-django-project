from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q, Avg
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import csv
import json

from .models import Book, Author, Work, BookAuthor, UserBook
from .forms import BookForm, AuthorForm, WorkForm, SignUpForm


# ============================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ============================================

def get_stats():
    """Получить статистику для главной страницы"""
    return {
        'books_count': Book.objects.count(),
        'authors_count': Author.objects.count(),
        'works_count': Work.objects.count(),
    }


# ============================================
# ОСНОВНЫЕ СТРАНИЦЫ
# ============================================

def main(request):
    """Главная страница с поиском"""
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'works')
    context = {'stats': get_stats()}

    if query:
        if search_type == 'works':
            works = Work.objects.select_related('author', 'book').filter(
                Q(title__icontains=query) | Q(author__last_name__icontains=query) | Q(
                    author__first_name__icontains=query)
            )
            context['works'] = works[:50]
            context['results_count'] = works.count()
        elif search_type == 'books':
            books = Book.objects.filter(
                Q(title__icontains=query) | Q(inventory_number__icontains=query)
            ).prefetch_related('authors')
            context['books'] = books[:50]
            context['results_count'] = books.count()
        elif search_type == 'authors':
            authors = Author.objects.filter(
                Q(last_name__icontains=query) | Q(first_name__icontains=query) | Q(middle_name__icontains=query)
            )
            context['authors'] = authors[:50]
            context['results_count'] = authors.count()

        context['query'] = query
        context['search_type'] = search_type
    else:
        context['recent_books'] = Book.objects.order_by('-id')[:10]

    return render(request, 'main.html', context)


def all_books(request):
    """Список всех книг с пагинацией"""
    books_list = Book.objects.all().prefetch_related('authors')
    paginator = Paginator(books_list, 12)
    page_number = request.GET.get('page')
    books = paginator.get_page(page_number)
    return render(request, 'all_books.html', {'page_obj': books})


def all_authors(request):
    """Список всех авторов с пагинацией"""
    authors_list = Author.objects.all()
    paginator = Paginator(authors_list, 12)
    page_number = request.GET.get('page')
    authors = paginator.get_page(page_number)
    return render(request, 'all_authors.html', {'page_obj': authors})


def book_detail(request, book_id):
    """Страница книги"""
    book = get_object_or_404(Book, id=book_id)
    works = book.works.all().select_related('author')
    book_authors = book.book_authors.select_related('author')

    # Проверка в избранном
    is_favorited = False
    if request.user.is_authenticated:
        is_favorited = UserBook.objects.filter(user=request.user, book=book).exists()

    context = {
        'book': book,
        'works': works,
        'book_authors': book_authors,
        'is_favorited': is_favorited,
    }
    return render(request, 'book_detail.html', context)


def author_detail(request, author_id):
    """Страница автора"""
    author = get_object_or_404(Author, id=author_id)
    books = author.books.all()
    works = author.works.all().select_related('book')

    context = {
        'author': author,
        'books': books,
        'works': works,
    }
    return render(request, 'author_detail.html', context)


def advanced_search(request):
    """Расширенный поиск"""
    query = request.GET.get('q', '').strip()
    work_type = request.GET.get('work_type', '')
    year_from = request.GET.get('year_from', '')
    year_to = request.GET.get('year_to', '')

    works = Work.objects.select_related('author', 'book')

    if query:
        works = works.filter(
            Q(title__icontains=query) | Q(author__last_name__icontains=query)
        )

    if work_type:
        works = works.filter(work_type=work_type)

    if year_from:
        works = works.filter(publication_year__gte=year_from)

    if year_to:
        works = works.filter(publication_year__lte=year_to)

    context = {
        'works': works,
        'query': query,
        'work_type': work_type,
        'year_from': year_from,
        'year_to': year_to,
    }
    return render(request, 'advanced_search.html', context)


def search_results(request):
    """Результаты расширенного поиска"""
    # Аналогично advanced_search, но с другим шаблоном
    return advanced_search(request)


# ============================================
# АВТОРИЗАЦИЯ
# ============================================

def signup(request):
    """Регистрация пользователя"""
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешна! Добро пожаловать!')
            return redirect('main')
        else:
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = SignUpForm()

    return render(request, 'signup.html', {'form': form})


def user_login(request):
    """Вход в систему"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('main')
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')

    return render(request, 'login.html')


@login_required
def user_logout(request):
    """Выход из системы"""
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('main')


# ============================================
# ДОБАВЛЕНИЕ
# ============================================

@login_required
def add_book(request):
    """Добавление книги"""
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            author_ids = request.POST.getlist('authors')
            for author_id in author_ids:
                BookAuthor.objects.create(
                    book=book,
                    author_id=author_id,
                    role='author'
                )
            messages.success(request, f'Книга "{book.title}" добавлена!')
            return redirect('book_detail', book_id=book.id)
    else:
        form = BookForm()

    authors = Author.objects.all()
    return render(request, 'add_book.html', {'form': form, 'authors': authors, 'title': 'Добавление книги'})


@login_required
def add_author(request):
    """Добавление автора"""
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            author = form.save()
            messages.success(request, f'Автор "{author.full_name}" добавлен!')
            return redirect('author_detail', author_id=author.id)
    else:
        form = AuthorForm()

    return render(request, 'add_author.html', {'form': form, 'title': 'Добавление автора'})


@login_required
def add_work(request, book_id):
    """Добавление произведения в книгу"""
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = WorkForm(request.POST)
        if form.is_valid():
            work = form.save(commit=False)
            work.book = book  # КЛЮЧЕВАЯ СТРОКА!
            work.save()
            messages.success(request, f'Произведение "{work.title}" добавлено в сборник!')
            return redirect('book_detail', book_id=book.id)
        else:
            messages.error(request, f'Ошибка: {form.errors}')
    else:
        form = WorkForm()

    context = {
        'form': form,
        'book': book,
        'title': f'Добавление произведения в "{book.title}"'
    }
    return render(request, 'add_work.html', context)


@login_required
def add_book_author(request, book_id):
    """Назначение автора книге"""
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        author_id = request.POST.get('author')
        role = request.POST.get('role', 'author')

        if author_id:
            BookAuthor.objects.create(
                book=book,
                author_id=author_id,
                role=role
            )
            messages.success(request, 'Автор назначен книге!')
            return redirect('book_detail', book_id=book.id)

    authors = Author.objects.exclude(id__in=book.authors.values_list('id', flat=True))
    return render(request, 'add_book_author.html', {
        'book': book,
        'authors': authors,
        'title': 'Назначение автора'
    })


# ============================================
# РЕДАКТИРОВАНИЕ
# ============================================

@login_required
def edit_book(request, book_id):
    """Редактирование книги"""
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            book = form.save()

            # Обновляем авторов
            book.authors.clear()
            author_ids = request.POST.getlist('authors')
            for author_id in author_ids:
                BookAuthor.objects.create(
                    book=book,
                    author_id=author_id,
                    role='author'
                )

            messages.success(request, 'Книга обновлена!')
            return redirect('book_detail', book_id=book.id)
    else:
        form = BookForm(instance=book)

    authors = Author.objects.all()
    selected_authors = book.authors.values_list('id', flat=True)

    context = {
        'form': form,
        'book': book,
        'authors': authors,
        'selected_authors': selected_authors,
        'title': 'Редактирование книги'
    }
    return render(request, 'edit_book.html', context)


@login_required
def edit_author(request, author_id):
    """Редактирование автора"""
    author = get_object_or_404(Author, id=author_id)

    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            author = form.save()
            messages.success(request, 'Автор обновлен!')
            return redirect('author_detail', author_id=author.id)
    else:
        form = AuthorForm(instance=author)

    return render(request, 'edit_author.html', {
        'form': form,
        'author': author,
        'title': 'Редактирование автора'
    })


@login_required
def edit_work(request, work_id):
    """Редактирование произведения"""
    work = get_object_or_404(Work, id=work_id)

    if request.method == 'POST':
        form = WorkForm(request.POST, instance=work)
        if form.is_valid():
            form.save()
            messages.success(request, 'Произведение обновлено!')
            return redirect('book_detail', book_id=work.book.id)
    else:
        form = WorkForm(instance=work)

    return render(request, 'edit_work.html', {
        'form': form,
        'work': work,
        'title': 'Редактирование произведения'
    })


# ============================================
# УДАЛЕНИЕ
# ============================================

@login_required
def delete_book(request, book_id):
    """Удаление книги"""
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        title = book.title
        book.delete()
        messages.success(request, f'Книга "{title}" удалена.')
        return redirect('all_books')

    return render(request, 'confirm_delete_book.html', {'book': book, 'title': 'Удаление книги'})


@login_required
def delete_author(request, author_id):
    """Удаление автора"""
    author = get_object_or_404(Author, id=author_id)

    works_count = author.works.count()
    books_count = author.books.count()

    if request.method == 'POST':
        full_name = author.full_name
        author.delete()
        messages.success(request, f'Автор "{full_name}" удален.')
        return redirect('all_authors')

    return render(request, 'confirm_delete_author.html', {
        'author': author,
        'works_count': works_count,
        'books_count': books_count,
        'title': 'Удаление автора'
    })


@login_required
def delete_work(request, work_id):
    """Удаление произведения"""
    work = get_object_or_404(Work, id=work_id)

    if request.method == 'POST':
        title = work.title
        book_id = work.book.id
        work.delete()
        messages.success(request, f'Произведение "{title}" удалено.')
        return redirect('book_detail', book_id=book_id)

    return render(request, 'confirm_delete.html', {'work': work})


# ============================================
# НОВЫЕ ФУНКЦИИ
# ============================================

# === АДМИН-ПАНЕЛЬ ===

@login_required
def admin_dashboard(request):
    """Административная панель"""
    if not request.user.is_staff:
        messages.error(request, 'Доступ запрещен. Требуются права администратора.')
        return redirect('main')

    context = {
        'total_books': Book.objects.count(),
        'total_authors': Author.objects.count(),
        'total_works': Work.objects.count(),
        'total_users': User.objects.count(),
        'recent_books': Book.objects.order_by('-id')[:10],
        'recent_users': User.objects.order_by('-date_joined')[:10],
        'books_by_year': Book.objects.values('publication_year').annotate(count=Count('id')).order_by(
            '-publication_year'),
        'most_popular_authors': Author.objects.annotate(
            book_count=Count('book')
        ).order_by('-book_count')[:5],
    }
    return render(request, 'admin_dashboard.html', context)


# === ИЗБРАННОЕ ===

@login_required
def favorites_view(request):
    """Страница избранного"""
    favorites = UserBook.objects.filter(user=request.user).select_related('book')
    return render(request, 'favorites.html', {'favorites': favorites})


@login_required
def add_to_favorites(request, book_id):
    """Добавить книгу в избранное"""
    book = get_object_or_404(Book, id=book_id)
    favorite, created = UserBook.objects.get_or_create(
        user=request.user,
        book=book
    )
    if created:
        messages.success(request, f'Книга "{book.title}" добавлена в избранное!')
    else:
        messages.info(request, f'Книга уже в избранном.')
    return redirect('book_detail', book_id=book.id)


@login_required
def remove_from_favorites(request, book_id):
    """Удалить книгу из избранного"""
    book = get_object_or_404(Book, id=book_id)
    UserBook.objects.filter(user=request.user, book=book).delete()
    messages.success(request, f'Книга "{book.title}" удалена из избранного.')
    return redirect('favorites')


# === РЕЙТИНГ И РЕЦЕНЗИИ ===

@login_required
def rate_book(request, book_id):
    """Оценить книгу (AJAX)"""
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        rating = request.POST.get('rating')

        try:
            rating = int(rating)
            if 1 <= rating <= 5:
                favorite, created = UserBook.objects.get_or_create(
                    user=request.user,
                    book=book
                )
                favorite.rating = rating
                favorite.save()
                return JsonResponse({'success': True, 'rating': rating})
            else:
                return JsonResponse({'success': False, 'error': 'Рейтинг должен быть от 1 до 5'})
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Неверный формат рейтинга'})

    return JsonResponse({'success': False, 'error': 'Метод не разрешен'})


@login_required
def add_review(request, book_id):
    """Добавить рецензию на книгу"""
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        review = request.POST.get('review', '').strip()

        if review:
            favorite, created = UserBook.objects.get_or_create(
                user=request.user,
                book=book
            )
            favorite.review = review
            favorite.save()
            messages.success(request, 'Рецензия сохранена!')
        else:
            messages.error(request, 'Текст рецензии не может быть пустым.')

        return redirect('book_detail', book_id=book.id)


# === ЭКСПОРТ ===

def export_books_csv(request):
    """Экспорт всех книг в CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="books_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Инвентарный номер', 'Название', 'Авторы', 'Издательство', 'Год', 'Страниц', 'Описание'])

    for book in Book.objects.all():
        writer.writerow([
            book.inventory_number,
            book.title,
            book.get_authors_list(),
            book.publisher or '',
            book.publication_year or '',
            book.pages or '',
            book.description or ''
        ])

    return response


def export_authors_csv(request):
    """Экспорт всех авторов в CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="authors_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Фамилия', 'Имя', 'Отчество', 'Год рождения', 'Год смерти', 'Биография'])

    for author in Author.objects.all():
        writer.writerow([
            author.last_name,
            author.first_name,
            author.middle_name or '',
            author.birth_year or '',
            author.death_year or '',
            author.biography or ''
        ])

    return response


def export_works_csv(request):
    """Экспорт всех произведений в CSV"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="works_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Название', 'Оригинальное название', 'Автор', 'Тип', 'Сборник', 'Страницы', 'Год публикации'])

    for work in Work.objects.select_related('author', 'book'):
        writer.writerow([
            work.title,
            work.original_title or '',
            work.author.full_name,
            work.get_work_type_display(),
            work.book.title,
            work.page_range or '',
            work.publication_year or ''
        ])

    return response


def export_all_data(request):
    """Экспорт всех данных в ZIP"""
    # Для простоты пока экспортируем только книги
    return export_books_csv(request)


# === PWA ===

def service_worker(request):
    """Service Worker для PWA"""
    return render(request, 'sw.js', content_type='application/javascript')


def manifest(request):
    """Манифест PWA"""
    return render(request, 'manifest.json', content_type='application/json')


# === КАСТОМНЫЕ ОБРАБОТЧИКИ ОШИБОК ===

def custom_404(request, exception):
    """Кастомная страница 404"""
    return render(request, '404.html', status=404)


def custom_500(request):
    """Кастомная страница 500"""
    return render(request, '500.html', status=500)