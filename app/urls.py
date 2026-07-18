from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/all/', views.all_books, name='all_books'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('authors/add/', views.add_author, name='add_author'),
    path('authors/all/', views.all_authors, name='all_authors'),
    path('authors/<int:author_id>/', views.author_detail, name='author_detail'),
    path('authors/<int:author_id>/edit/', views.edit_author, name='edit_author'),
    path('authors/<int:author_id>/delete/', views.delete_author, name='delete_author'),
    path('books/<int:book_id>/add-author/', views.add_book_author, name='add_book_author'),
    path('books/<int:book_id>/add-work/', views.add_work, name='add_work'),
    path('works/<int:work_id>/edit/', views.edit_work, name='edit_work'),
    path('works/<int:work_id>/delete/', views.delete_work, name='delete_work'),
    path('search/advanced/', views.search_advanced, name='advanced_search'),
]