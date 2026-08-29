from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, Author, Work, BookAuthor


class AuthorSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Author
        fields = ['id', 'last_name', 'first_name', 'middle_name', 'full_name', 'birth_year', 'death_year', 'biography']


class WorkSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field='full_name', read_only=True)
    book = serializers.SlugRelatedField(slug_field='title', read_only=True)

    class Meta:
        model = Work
        fields = ['id', 'title', 'original_title', 'work_type', 'author', 'book', 'first_page', 'last_page',
                  'publication_year', 'description']


class BookSerializer(serializers.ModelSerializer):
    authors = AuthorSerializer(many=True, read_only=True)
    authors_list = serializers.SerializerMethodField()
    works = WorkSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'inventory_number', 'publisher',
            'publication_year', 'pages', 'description',
            'cover_image', 'authors', 'authors_list', 'works',
            'created_at'
        ]

    def get_authors_list(self, obj):
        return obj.get_authors_list()


class BookCreateUpdateSerializer(serializers.ModelSerializer):
    author_ids = serializers.ListField(write_only=True, required=False)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'inventory_number', 'publisher',
            'publication_year', 'pages', 'description',
            'cover_image', 'author_ids'
        ]

    def create(self, validated_data):
        author_ids = validated_data.pop('author_ids', [])
        book = Book.objects.create(**validated_data)

        for author_id in author_ids:
            BookAuthor.objects.create(book=book, author_id=author_id)

        return book

    def update(self, instance, validated_data):
        author_ids = validated_data.pop('author_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if author_ids is not None:
            instance.authors.clear()
            for author_id in author_ids:
                BookAuthor.objects.create(book=instance, author_id=author_id)

        return instance


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user