from django.test import TestCase
from django.contrib.auth.models import User
from .models import Author, Book, Work

class AuthorModelTest(TestCase):
    def test_author_creation(self):
        author = Author.objects.create(
            last_name='Пушкин',
            first_name='Александр',
            middle_name='Сергеевич',
            birth_year=1799,
            death_year=1837
        )
        self.assertEqual(author.full_name, 'Пушкин Александр Сергеевич')
        self.assertEqual(author.years_lived, '1799-1837')

class BookModelTest(TestCase):
    def test_book_creation(self):
        book = Book.objects.create(
            title='Евгений Онегин',
            inventory_number='00001',
            publisher='Наука',
            publication_year=2020,
            pages=350
        )
        self.assertEqual(str(book), '[00001] Евгений Онегин')