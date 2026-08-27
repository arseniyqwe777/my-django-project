import pytest
from django.test import Client

@pytest.fixture
def client():
    return Client()

@pytest.mark.skip(reason="Python 3.14 compatibility issue with Django Context.copy()")
@pytest.mark.django_db
def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200

@pytest.mark.skip(reason="Python 3.14 compatibility issue with Django Context.copy()")
@pytest.mark.django_db
def test_books_page(client):
    response = client.get('/books/')
    assert response.status_code == 200

@pytest.mark.skip(reason="Python 3.14 compatibility issue with Django Context.copy()")
@pytest.mark.django_db
def test_signup_page(client):
    response = client.get('/signup/')
    assert response.status_code == 200