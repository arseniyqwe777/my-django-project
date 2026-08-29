from rest_framework import viewsets, status, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.throttling import AnonRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth.models import User
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import Book, Author, Work
from .serializers import (
    BookSerializer, BookCreateUpdateSerializer,
    AuthorSerializer, WorkSerializer,
    UserSerializer, RegisterSerializer
)


class BookViewSet(viewsets.ModelViewSet):
    """API для управления книгами"""
    queryset = Book.objects.all().prefetch_related('authors', 'works', 'works__author')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['publication_year', 'publisher']
    search_fields = ['title', 'inventory_number', 'publisher']
    ordering_fields = ['title', 'publication_year', 'created_at']

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return BookCreateUpdateSerializer
        return BookSerializer

    @action(detail=True, methods=['get'])
    def works(self, request, pk=None):
        """Получить все произведения книги"""
        book = self.get_object()
        works = book.works.all().select_related('author')
        serializer = WorkSerializer(works, many=True)
        return Response(serializer.data)


class AuthorViewSet(viewsets.ModelViewSet):
    """API для управления авторами"""
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['last_name', 'first_name', 'middle_name']
    ordering_fields = ['last_name', 'birth_year']

    @action(detail=True, methods=['get'])
    def books(self, request, pk=None):
        """Получить все книги автора"""
        author = self.get_object()
        books = author.books.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


class WorkViewSet(viewsets.ModelViewSet):
    """API для управления произведениями"""
    queryset = Work.objects.all().select_related('author', 'book')
    serializer_class = WorkSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['work_type', 'publication_year']
    search_fields = ['title', 'original_title', 'author__last_name']

    @action(detail=False, methods=['get'])
    def by_book(self, request):
        """Получить произведения по ID книги"""
        book_id = request.query_params.get('book_id')
        if book_id:
            works = self.queryset.filter(book_id=book_id)
            serializer = self.get_serializer(works, many=True)
            return Response(serializer.data)
        return Response({'error': 'book_id required'}, status=400)


class RegisterView(APIView):
    """Регистрация пользователя через API"""
    permission_classes = [permissions.AllowAny]
    throttle_classes = [AnonRateThrottle]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'user': UserSerializer(user).data,
                'message': 'User created successfully'
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MeView(APIView):
    """Текущий пользователь"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)