from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from . import views
from .api_views import BookViewSet, AuthorViewSet, WorkViewSet, RegisterView, MeView


# ============================================
# HEALTH-CHECK
# ============================================

def health_check(request):
    """Health-check для мониторинга"""
    return JsonResponse({
        'status': 'ok',
        'database': 'connected',
        'redis': 'connected'
    })


# ============================================
# API Router
# ============================================

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='api-book')
router.register(r'authors', AuthorViewSet, basename='api-author')
router.register(r'works', WorkViewSet, basename='api-work')


# ============================================
# Swagger документация
# ============================================

schema_view = get_schema_view(
    openapi.Info(
        title="BookBridge API",
        default_version='v1',
        description="API для управления библиотекой BookBridge",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="support@bookbridge.ru"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)


# ============================================
# API маршруты
# ============================================

api_urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/register/', RegisterView.as_view(), name='api_register'),
    path('auth/me/', MeView.as_view(), name='api_me'),
]


# ============================================
# Основные маршруты
# ============================================

urlpatterns = [
    # === HEALTH-CHECK ===
    path('health/', health_check, name='health'),

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

    # === АНАЛИТИКА ===
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('api/analytics/', views.analytics_data, name='analytics_data'),

    # === API ===
    path('api/', include(api_urlpatterns)),

    # === SWAGGER ДОКУМЕНТАЦИЯ ===
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Для отображения медиафайлов в разработке
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Обработчики ошибок
handler404 = 'app.views.custom_404'
handler500 = 'app.views.custom_500'