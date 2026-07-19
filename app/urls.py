from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # === ОСНОВНЫЕ СТРАНИЦЫ ===
    path('', views.main, name='main'),
    path('books/', views.all_books, name='all_books'),
    path('authors/', views.all_authors, name='all_authors'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('author/<int:author_id>/', views.author_detail, name='author_detail'),
    path('advanced-search/', views.advanced_search, name='advanced_search'),
    path('search-results/', views.search_results, name='search_results'),

    # === АВТОРИЗАЦИЯ ===
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # === ДОБАВЛЕНИЕ ===
    path('add-book/', views.add_book, name='add_book'),
    path('add-author/', views.add_author, name='add_author'),
    path('add-work/<int:book_id>/', views.add_work, name='add_work'),
    path('add-book-author/<int:book_id>/', views.add_book_author, name='add_book_author'),

    # === РЕДАКТИРОВАНИЕ ===
    path('edit-book/<int:book_id>/', views.edit_book, name='edit_book'),
    path('edit-author/<int:author_id>/', views.edit_author, name='edit_author'),
    path('edit-work/<int:work_id>/', views.edit_work, name='edit_work'),

    # === УДАЛЕНИЕ ===
    path('delete-book/<int:book_id>/', views.delete_book, name='delete_book'),
    path('delete-author/<int:author_id>/', views.delete_author, name='delete_author'),
    path('delete-work/<int:work_id>/', views.delete_work, name='delete_work'),

    # ============================================
    # НОВЫЕ МАРШРУТЫ
    # ============================================

    # === АДМИН-ПАНЕЛЬ ===
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # === ИЗБРАННОЕ ===
    path('favorites/', views.favorites_view, name='favorites'),
    path('favorites/add/<int:book_id>/', views.add_to_favorites, name='add_to_favorites'),
    path('favorites/remove/<int:book_id>/', views.remove_from_favorites, name='remove_from_favorites'),

    # === РЕЙТИНГ И РЕЦЕНЗИИ ===
    path('rate/<int:book_id>/', views.rate_book, name='rate_book'),
    path('review/<int:book_id>/', views.add_review, name='add_review'),

    # === ЭКСПОРТ ===
    path('export/books/', views.export_books_csv, name='export_books_csv'),
    path('export/authors/', views.export_authors_csv, name='export_authors_csv'),
    path('export/works/', views.export_works_csv, name='export_works_csv'),
    path('export/all/', views.export_all_data, name='export_all_data'),

    # === PWA ===
    path('sw.js/', views.service_worker, name='service_worker'),
    path('manifest.json/', views.manifest, name='manifest'),
]

# Для отображения медиафайлов в разработке
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Обработчики ошибок
handler404 = 'app.views.custom_404'
handler500 = 'app.views.custom_500'