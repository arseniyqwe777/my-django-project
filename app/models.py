from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Author(models.Model):
    """Модель автора"""
    last_name = models.CharField('Фамилия', max_length=100)
    first_name = models.CharField('Имя', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100, blank=True, null=True)
    birth_year = models.IntegerField('Год рождения', blank=True, null=True)
    death_year = models.IntegerField('Год смерти', blank=True, null=True)
    biography = models.TextField('Биография', blank=True)

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        if self.middle_name:
            return f'{self.last_name} {self.first_name} {self.middle_name}'
        return f'{self.last_name} {self.first_name}'

    @property
    def years_lived(self):
        if self.birth_year and self.death_year:
            return f'{self.birth_year}–{self.death_year}'
        elif self.birth_year:
            return f'р. {self.birth_year}'
        return ''


class Book(models.Model):
    """Модель книги"""
    title = models.CharField('Название', max_length=255)
    inventory_number = models.CharField('Инвентарный номер', max_length=10, unique=True)
    publisher = models.CharField('Издательство', max_length=200, blank=True)
    publication_year = models.IntegerField('Год издания', blank=True, null=True)
    pages = models.IntegerField('Количество страниц', blank=True, null=True)
    description = models.TextField('Описание', blank=True)
    cover_image = models.ImageField('Обложка', upload_to='covers/', blank=True, null=True)
    authors = models.ManyToManyField(Author, through='BookAuthor', related_name='books')

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_authors_list(self):
        return ', '.join([author.full_name for author in self.authors.all()])


class BookAuthor(models.Model):
    """Связь книга-автор с ролью"""
    ROLE_CHOICES = [
        ('author', 'Автор'),
        ('compiler', 'Составитель'),
        ('editor', 'Редактор'),
        ('translator', 'Переводчик'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='book_authors')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='author_books')
    role = models.CharField('Роль', max_length=20, choices=ROLE_CHOICES, default='author')

    class Meta:
        verbose_name = 'Автор книги'
        verbose_name_plural = 'Авторы книг'
        unique_together = ('book', 'author', 'role')

    def __str__(self):
        return f'{self.author.full_name} — {self.get_role_display()}'


class Work(models.Model):
    """Модель произведения в сборнике"""
    WORK_TYPE_CHOICES = [
        ('novel', 'Роман'),
        ('story', 'Рассказ'),
        ('novella', 'Повесть'),
        ('short_story', 'Новелла'),
        ('poem', 'Стихотворение'),
        ('ballad', 'Баллада'),
        ('fairy_tale', 'Сказка'),
        ('play', 'Пьеса'),
        ('article', 'Статья'),
        ('essay', 'Эссе'),
        ('memoirs', 'Мемуары'),
        ('biography', 'Биография'),
        ('chapter', 'Глава'),
        ('excerpt', 'Отрывок'),
        ('other', 'Другое'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='works')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='works')
    title = models.CharField('Название произведения', max_length=255)
    original_title = models.CharField('Оригинальное название', max_length=255, blank=True)
    work_type = models.CharField('Тип произведения', max_length=20, choices=WORK_TYPE_CHOICES, default='other')
    first_page = models.IntegerField('Страница начала', blank=True, null=True)
    last_page = models.IntegerField('Страница конца', blank=True, null=True)
    publication_year = models.IntegerField('Год первой публикации', blank=True, null=True)
    description = models.TextField('Краткое содержание', blank=True)

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def page_range(self):
        if self.first_page and self.last_page:
            return f'{self.first_page}-{self.last_page}'
        elif self.first_page:
            return f'стр. {self.first_page}'
        return ''


# ============================================
# НОВАЯ МОДЕЛЬ ДЛЯ ИЗБРАННОГО
# ============================================

class UserBook(models.Model):
    """Избранные книги и рейтинги пользователей"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    rating = models.IntegerField(
        'Рейтинг',
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Рейтинг от 1 до 5'
    )
    review = models.TextField(
        'Рецензия',
        blank=True,
        help_text='Ваша рецензия на книгу'
    )
    added_at = models.DateTimeField('Дата добавления', auto_now_add=True)

    class Meta:
        verbose_name = 'Избранная книга'
        verbose_name_plural = 'Избранные книги'
        unique_together = ('user', 'book')
        ordering = ['-added_at']

    def __str__(self):
        return f'{self.user.username} -> {self.book.title}'