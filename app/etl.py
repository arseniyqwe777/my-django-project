import pandas as pd
from django.db import connection
from django.utils import timezone
from datetime import timedelta
from .models import Book, BookStat


def collect_daily_stats():
    """Собрать статистику за последний день"""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)

    # SQL запрос с оконными функциями
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                b.id,
                b.title,
                COUNT(DISTINCT ub.user_id) as favorites_count,
                COUNT(DISTINCT w.id) as works_count
            FROM app_book b
            LEFT JOIN app_userbook ub ON b.id = ub.book_id
            LEFT JOIN app_work w ON b.id = w.book_id
            WHERE b.created_at >= %s
            GROUP BY b.id, b.title
        """, [yesterday])

        results = cursor.fetchall()

    # Обновляем статистику
    for book_id, title, favorites, works in results:
        stat, created = BookStat.objects.get_or_create(
            book_id=book_id,
            date=today,
            defaults={
                'views': 0,
                'favorites': favorites or 0,
            }
        )
        if not created:
            stat.favorites = favorites or 0
            stat.save()

    return len(results)


def get_weekly_stats():
    """Получить недельную статистику"""
    week_ago = timezone.now().date() - timedelta(days=7)

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                date,
                SUM(views) as total_views,
                SUM(favorites) as total_favorites,
                COUNT(DISTINCT book_id) as active_books
            FROM app_bookstat
            WHERE date >= %s
            GROUP BY date
            ORDER BY date
        """, [week_ago])

        return cursor.fetchall()


def get_top_books(limit=10):
    """Получить топ книг по просмотрам"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                b.id,
                b.title,
                COUNT(bs.id) as days,
                SUM(bs.views) as total_views,
                SUM(bs.favorites) as total_favorites
            FROM app_book b
            LEFT JOIN app_bookstat bs ON b.id = bs.book_id
            GROUP BY b.id, b.title
            ORDER BY total_views DESC
            LIMIT %s
        """, [limit])

        return cursor.fetchall()