from django import forms
from .models import Book, Author, Work, BookAuthor


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'inventory_number', 'publisher', 'publication_year',
                  'pages', 'description', 'cover_image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите полное название книги'}),
            'inventory_number': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': '00001', 'maxlength': '5'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Название издательства'}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '2024'}),
            'pages': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '350'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean_inventory_number(self):
        inventory_number = self.cleaned_data.get('inventory_number')
        if inventory_number:
            if not inventory_number.isdigit():
                raise forms.ValidationError('Инвентарный номер должен содержать только цифры')
            if len(inventory_number) != 5:
                raise forms.ValidationError('Инвентарный номер должен быть пятизначным')
        return inventory_number


class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['last_name', 'first_name', 'middle_name', 'birth_year', 'death_year', 'biography']
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Толстой'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Лев'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Николаевич'}),
            'birth_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1828'}),
            'death_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1910'}),
            'biography': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }


class WorkForm(forms.ModelForm):
    class Meta:
        model = Work
        fields = ['title', 'original_title', 'work_type', 'first_page', 'last_page',
                  'description', 'publication_year', 'author']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Война и мир'}),
            'original_title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'War and Peace'}),
            'work_type': forms.Select(attrs={'class': 'form-select'}),
            'first_page': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '5'}),
            'last_page': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '25'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'publication_year': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1869'}),
            'author': forms.Select(attrs={'class': 'form-select'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        first_page = cleaned_data.get('first_page')
        last_page = cleaned_data.get('last_page')
        if first_page and last_page and first_page >= last_page:
            raise forms.ValidationError('Страница начала должна быть меньше страницы конца')
        return cleaned_data


class BookAuthorForm(forms.ModelForm):
    class Meta:
        model = BookAuthor
        fields = ['author', 'role']
        widgets = {
            'author': forms.Select(attrs={'class': 'form-select'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
        }