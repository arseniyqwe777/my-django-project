import pytest
from django.contrib.auth.models import User
from app.models import Book, Author, Work

@pytest.mark.django_db
def test_create_book():
    book = Book.objects.create(
        title="Test Book",
        inventory_number="00001",
        publisher="Test Publisher",
        publication_year=2024,
        pages=100
    )
    assert book.title == "Test Book"
    assert str(book) == "Test Book"

@pytest.mark.django_db
def test_create_author():
    author = Author.objects.create(
        last_name="Пушкин",
        first_name="Александр",
        middle_name="Сергеевич",
        birth_year=1799,
        death_year=1837
    )
    assert author.full_name == "Пушкин Александр Сергеевич"
    assert "1799" in author.years_lived and "1837" in author.years_lived
@pytest.mark.django_db
def test_book_author_relationship():
    book = Book.objects.create(title="Евгений Онегин", inventory_number="00002")
    author = Author.objects.create(last_name="Пушкин", first_name="Александр")
    book.authors.add(author)
    assert book.authors.count() == 1
    assert book.get_authors_list() == "Пушкин Александр"