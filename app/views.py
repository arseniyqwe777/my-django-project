from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.db import IntegrityError
from .models import Book, Author, Work, BookAuthor
from .forms import BookForm, AuthorForm, WorkForm, BookAuthorForm


def main(request):
    """
    Главная страница с поиском произведений
    """
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'works')

    books = None
    authors = None
    works = None
    results_count = 0

    if query:
        if search_type == 'works':
            works = Work.objects.filter(
                Q(title__icontains=query) |
                Q(author__last_name__icontains=query) |
                Q(author__first_name__icontains=query) |
                Q(description__icontains=query)
            ).select_related('book', 'author')
            results_count = works.count()

        elif search_type == 'books':
            books = Book.objects.filter(
                Q(title__icontains=query) |
                Q(inventory_number__icontains=query) |
                Q(authors__last_name__icontains=query) |
                Q(authors__first_name__icontains=query) |
                Q(publisher__icontains=query)
            ).distinct()
            results_count = books.count()

        elif search_type == 'authors':
            authors = Author.objects.filter(
                Q(last_name__icontains=query) |
                Q(first_name__icontains=query) |
                Q(middle_name__icontains=query)
            )
            results_count = authors.count()

    recent_books = Book.objects.all().order_by('-id')[:5]

    stats = {
        'books_count': Book.objects.count(),
        'authors_count': Author.objects.count(),
        'works_count': Work.objects.count(),
    }

    context = {
        'query': query,
        'search_type': search_type,
        'books': books,
        'authors': authors,
        'works': works,
        'results_count': results_count,
        'recent_books': recent_books,
        'stats': stats,
    }
    return render(request, 'main.html', context)


def signup(request):
    """
    Регистрация нового пользователя
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email', '')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if password != password2:
            messages.error(request, 'Пароли не совпадают')
            return render(request, 'signup.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует')
            return render(request, 'signup.html')

        if len(password) < 6:
            messages.error(request, 'Пароль должен содержать минимум 6 символов')
            return render(request, 'signup.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        auth_login(request, user)
        messages.success(request, f'Добро пожаловать, {username}!')
        return redirect('main')

    return render(request, 'signup.html')


def login(request):
    """
    Вход в систему
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f'С возвращением, {username}!')
            next_url = request.GET.get('next', 'main')
            return redirect(next_url)
        else:
            messages.error(request, 'Неверное имя пользователя или пароль')

    return render(request, 'login.html')


def logout(request):
    """
    Выход из системы
    """
    auth_logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('main')


@login_required
def add_book(request):
    """
    Добавление новой книги с защитой от дублирования
    """
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            inventory_number = form.cleaned_data.get('inventory_number')
            if Book.objects.filter(inventory_number=inventory_number).exists():
                messages.error(request, f'Книга с инвентарным номером {inventory_number} уже существует!')
                return render(request, 'add_book.html', {'form': form, 'authors': Author.objects.all()})

            try:
                book = form.save()
                messages.success(request, f'Книга "{book.title}" (инв. №{book.inventory_number}) успешно добавлена!')

                author_ids = request.POST.getlist('authors')
                unique_author_ids = list(dict.fromkeys(author_ids))

                for author_id in unique_author_ids:
                    if author_id:
                        book.authors.add(author_id)

                return redirect('book_detail', book_id=book.id)
            except IntegrityError:
                messages.error(request, 'Ошибка при сохранении книги. Попробуйте еще раз.')
                return render(request, 'add_book.html', {'form': form, 'authors': Author.objects.all()})
        else:
            messages.error(request, 'Ошибка при добавлении книги. Проверьте форму.')
    else:
        form = BookForm()

    context = {
        'form': form,
        'authors': Author.objects.all(),
        'title': 'Добавление книги'
    }
    return render(request, 'add_book.html', context)


@login_required
def edit_book(request, book_id):
    """
    Редактирование книги с защитой от дублирования
    """
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            inventory_number = form.cleaned_data.get('inventory_number')
            if Book.objects.filter(inventory_number=inventory_number).exclude(id=book.id).exists():
                messages.error(request, f'Книга с инвентарным номером {inventory_number} уже существует!')
                return render(request, 'edit_book.html', {'form': form, 'book': book, 'authors': Author.objects.all()})

            try:
                book = form.save()
                messages.success(request, f'Книга "{book.title}" успешно обновлена!')

                book.authors.clear()
                author_ids = request.POST.getlist('authors')
                unique_author_ids = list(dict.fromkeys(author_ids))

                for author_id in unique_author_ids:
                    if author_id:
                        book.authors.add(author_id)

                return redirect('book_detail', book_id=book.id)
            except IntegrityError:
                messages.error(request, 'Ошибка при сохранении книги. Возможно, дублирование авторов.')
                return render(request, 'edit_book.html', {'form': form, 'book': book, 'authors': Author.objects.all()})
        else:
            messages.error(request, 'Ошибка при редактировании книги. Проверьте форму.')
    else:
        form = BookForm(instance=book)

    selected_authors = book.authors.values_list('id', flat=True)
    context = {
        'form': form,
        'book': book,
        'authors': Author.objects.all(),
        'selected_authors': selected_authors,
        'title': f'Редактирование книги: {book.title}'
    }
    return render(request, 'edit_book.html', context)


@login_required
def delete_book(request, book_id):
    """
    Удаление книги с защитой от повторного удаления
    """
    book = get_object_or_404(Book, id=book_id)
    book_title = book.title

    if request.method == 'POST':
        try:
            if Book.objects.filter(id=book_id).exists():
                book.works.all().delete()
                book.delete()
                messages.success(request, f'Книга "{book_title}" и все её произведения удалены!')
            else:
                messages.warning(request, f'Книга "{book_title}" уже была удалена.')
            return redirect('all_books')
        except Exception as e:
            messages.error(request, f'Ошибка при удалении книги: {str(e)}')
            return redirect('book_detail', book_id=book_id)

    context = {'book': book, 'title': 'Удаление книги'}
    return render(request, 'confirm_delete_book.html', context)


@login_required
def add_author(request):
    """
    Добавление нового автора с защитой от дублирования
    """
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            try:
                author = form.save()
                messages.success(request, f'Автор "{author.full_name}" успешно добавлен!')
                return redirect('author_detail', author_id=author.id)
            except IntegrityError:
                messages.error(request, 'Ошибка при добавлении автора. Возможно, такой автор уже существует.')
                return render(request, 'add_author.html', {'form': form})
        else:
            messages.error(request, 'Ошибка при добавлении автора. Проверьте форму.')
    else:
        form = AuthorForm()

    context = {
        'form': form,
        'title': 'Добавление автора'
    }
    return render(request, 'add_author.html', context)


@login_required
def edit_author(request, author_id):
    """
    Редактирование автора с защитой от дублирования
    """
    author = get_object_or_404(Author, id=author_id)

    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            try:
                author = form.save()
                messages.success(request, f'Автор "{author.full_name}" успешно обновлён!')
                return redirect('author_detail', author_id=author.id)
            except IntegrityError:
                messages.error(request, 'Ошибка при сохранении автора. Возможно, такой автор уже существует.')
                return render(request, 'edit_author.html', {'form': form, 'author': author})
        else:
            messages.error(request, 'Ошибка при редактировании автора. Проверьте форму.')
    else:
        form = AuthorForm(instance=author)

    context = {
        'form': form,
        'author': author,
        'title': f'Редактирование автора: {author.full_name}'
    }
    return render(request, 'edit_author.html', context)


@login_required
def delete_author(request, author_id):
    """
    Удаление автора с защитой от повторного удаления
    """
    author = get_object_or_404(Author, id=author_id)
    author_name = author.full_name
    works_count = author.works.count()
    books_count = author.books.count()

    if request.method == 'POST':
        if works_count > 0 or books_count > 0:
            messages.error(request,
                           f'Нельзя удалить автора "{author_name}", так как с ним связаны {works_count} произведений и {books_count} книг!')
            return redirect('author_detail', author_id=author.id)

        try:
            if Author.objects.filter(id=author_id).exists():
                author.delete()
                messages.success(request, f'Автор "{author_name}" успешно удалён!')
            else:
                messages.warning(request, f'Автор "{author_name}" уже был удалён.')
            return redirect('all_authors')
        except Exception as e:
            messages.error(request, f'Ошибка при удалении автора: {str(e)}')
            return redirect('author_detail', author_id=author_id)

    context = {
        'author': author,
        'works_count': works_count,
        'books_count': books_count,
        'title': 'Удаление автора'
    }
    return render(request, 'confirm_delete_author.html', context)


@login_required
def add_work(request, book_id):
    """
    Добавление произведения в книгу
    """
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = WorkForm(request.POST)
        if form.is_valid():
            try:
                work = form.save(commit=False)
                work.book = book
                work.save()
                messages.success(request, f'Произведение "{work.title}" добавлено в сборник!')
                return redirect('book_detail', book_id=book.id)
            except Exception as e:
                messages.error(request, f'Ошибка при сохранении: {str(e)}')
        else:
            messages.error(request, f'Ошибка валидации: {form.errors}')
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
    """
    Назначение автора книге с указанием роли
    """
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = BookAuthorForm(request.POST)
        if form.is_valid():
            try:
                book_author = form.save(commit=False)
                book_author.book = book
                book_author.save()
                messages.success(request, f'Автор назначен книге "{book.title}"')
                return redirect('book_detail', book_id=book.id)
            except IntegrityError:
                messages.error(request, 'Ошибка: такая связь автор-книга уже существует!')
                return render(request, 'add_book_author.html', {'form': form, 'book': book})
    else:
        form = BookAuthorForm()

    context = {
        'form': form,
        'book': book,
        'title': f'Назначение автора книге "{book.title}"'
    }
    return render(request, 'add_book_author.html', context)


def book_detail(request, book_id):
    """
    Детальная страница книги со списком произведений
    """
    book = get_object_or_404(Book, id=book_id)
    works = book.works.all().select_related('author')
    book_authors = BookAuthor.objects.filter(book=book).select_related('author')

    context = {
        'book': book,
        'works': works,
        'book_authors': book_authors,
    }
    return render(request, 'book_detail.html', context)


def author_detail(request, author_id):
    """
    Детальная страница автора
    """
    author = get_object_or_404(Author, id=author_id)
    works = author.works.all().select_related('book')
    books = author.books.all()

    context = {
        'author': author,
        'works': works,
        'books': books,
    }
    return render(request, 'author_detail.html', context)


@login_required
def edit_work(request, work_id):
    """
    Редактирование произведения с защитой от дублирования
    """
    work = get_object_or_404(Work, id=work_id)

    if request.method == 'POST':
        form = WorkForm(request.POST, instance=work)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'Произведение "{work.title}" обновлено!')
                return redirect('book_detail', book_id=work.book.id)
            except IntegrityError:
                messages.error(request, 'Ошибка при редактировании произведения. Попробуйте еще раз.')
        else:
            messages.error(request, 'Ошибка при редактировании произведения.')
    else:
        form = WorkForm(instance=work)

    context = {
        'form': form,
        'work': work,
        'title': 'Редактирование произведения'
    }
    return render(request, 'edit_work.html', context)


@login_required
def delete_work(request, work_id):
    """
    Удаление произведения с защитой от повторного удаления
    """
    work = get_object_or_404(Work, id=work_id)
    book_id = work.book.id
    work_title = work.title

    if request.method == 'POST':
        try:
            if Work.objects.filter(id=work_id).exists():
                work.delete()
                messages.success(request, f'Произведение "{work_title}" удалено!')
            else:
                messages.warning(request, f'Произведение "{work_title}" уже было удалено.')
            return redirect('book_detail', book_id=book_id)
        except Exception as e:
            messages.error(request, f'Ошибка при удалении произведения: {str(e)}')
            return redirect('book_detail', book_id=book_id)

    context = {'work': work}
    return render(request, 'confirm_delete.html', context)


def all_books(request):
    """
    Список всех книг с пагинацией
    """
    books_list = Book.objects.all().prefetch_related('authors')
    paginator = Paginator(books_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'Все книги'
    }
    return render(request, 'all_books.html', context)


def all_authors(request):
    """
    Список всех авторов с пагинацией
    """
    authors_list = Author.objects.all()
    paginator = Paginator(authors_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'title': 'Все авторы'
    }
    return render(request, 'all_authors.html', context)


def search_advanced(request):
    """
    Расширенный поиск
    """
    if request.method == 'GET' and request.GET.get('q'):
        query = request.GET.get('q')
        work_type = request.GET.get('work_type', '')
        year_from = request.GET.get('year_from', '')
        year_to = request.GET.get('year_to', '')

        works = Work.objects.all()

        if query:
            works = works.filter(Q(title__icontains=query) | Q(author__last_name__icontains=query))
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
        return render(request, 'search_results.html', context)

    return render(request, 'advanced_search.html')