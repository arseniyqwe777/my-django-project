from django.core.mail import send_mail
from django.conf import settingsfrom

django.template.loader
import render_to_string
from django.utils.html import strip_tags
from .models import Book, Author, Work


def send_notification_email(subject, template, context, recipient_list):
    """
    Отправка email-уведомления с использованием HTML-шаблона
    """
    try:
        html_message = render_to_string(template, context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            html_message=html_message,
            fail_silently=True,
        )
        return True
    except Exception as e:
        print(f"Ошибка отправки email: {e}")
        return False


def get_book_stats():
    """
    Получить статистику по книгам
    """
    from django.db.models import Avg

    return {
        'total_books': Book.objects.count(),
        'total_authors': Author.objects.count(),
        'total_works': Work.objects.count(),
        'avg_pages': Book.objects.aggregate(Avg('pages'))['pages__avg'] or 0,
        'oldest_book': Book.objects.order_by('publication_year').first(),
        'newest_book': Book.objects.order_by('-publication_year').first(),
    }


def get_top_authors(limit=5):
    """
    Получить топ авторов по количеству книг
    """
    from django.db.models import Count

    return Author.objects.annotate(
        book_count=Count('book')
    ).order_by('-book_count')[:limit]


def get_books_by_decade():
    """
    Сгруппировать книги по десятилетиям
    """
    books = Book.objects.exclude(publication_year__isnull=True)
    decades = {}

    for book in books:
        decade = (book.publication_year // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    return sorted(decades.items())