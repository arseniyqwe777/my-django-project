from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Author(models.Model):
    """
    Модель автора произведения
    """
    last_name = models.CharField('Фамилия', max_length=100)
    first_name = models.CharField('Имя', max_length=100)
    middle_name = models.CharField('Отчество', max_length=100, blank=True, null=True)
    birth_year = models.IntegerField('Год рождения', null=True, blank=True)
    death_year = models.IntegerField('Год смерти', null=True, blank=True)
    biography = models.TextField('Биография', blank=True, null=True)

    class Meta:
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        if self.middle_name:
            return f"{self.last_name} {self.first_name} {self.middle_name}"
        return f"{self.last_name} {self.first_name}"

    @property
    def full_name(self):
        return self.__str__()

    @property
    def years_lived(self):
        if self.birth_year and self.death_year:
            return f"{self.birth_year}-{self.death_year}"
        elif self.birth_year:
            return f"р. {self.birth_year}"
        elif self.death_year:
            return f"ум. {self.death_year}"
        return ""


class Book(models.Model):
    """
    Модель книги (сборника, хрестоматии)
    """
    title = models.CharField('Название книги', max_length=300)
    inventory_number = models.CharField(
        'Инвентарный номер',
        max_length=5,
        unique=True,
        help_text="Пятизначный инвентарный номер (например: 00001, 12345)"
    )
    publisher = models.CharField('Издательство', max_length=200, blank=True, null=True)
    publication_year = models.IntegerField('Год издания', null=True, blank=True)
    pages = models.IntegerField('Количество страниц', null=True, blank=True)
    description = models.TextField('Описание', blank=True, null=True)
    cover_image = models.ImageField('Обложка', upload_to='covers/', blank=True, null=True)

    authors = models.ManyToManyField(Author, through='BookAuthor', related_name='books')

    class Meta:
        verbose_name = 'Книга'
        verbose_name_plural = 'Книги'
        ordering = ['inventory_number']

    def __str__(self):
        return f"[{self.inventory_number}] {self.title}"

    def get_authors_list(self):
        return ", ".join([author.full_name for author in self.authors.all()])


class BookAuthor(models.Model):
    """
    Промежуточная модель для связи книга-автор с указанием роли
    """
    ROLE_CHOICES = [
        ('author', 'Автор'),
        ('compiler', 'Составитель'),
        ('editor', 'Редактор'),
        ('translator', 'Переводчик'),
        ('illustrator', 'Иллюстратор'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE, verbose_name='Книга')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, verbose_name='Автор')
    role = models.CharField('Роль', max_length=50, choices=ROLE_CHOICES, default='author')

    class Meta:
        verbose_name = 'Связь книга-автор'
        verbose_name_plural = 'Связи книга-автор'
        unique_together = ['book', 'author', 'role']

    def __str__(self):
        return f"{self.author.full_name} - {self.book.title} ({self.get_role_display()})"


class Work(models.Model):
    """
    Модель произведения внутри сборника с расширенными типами
    """
    WORK_TYPE_CHOICES = [
        # Художественная проза
        ('novel', 'Роман'),
        ('story', 'Рассказ'),
        ('novella', 'Повесть'),
        ('short_story', 'Новелла'),
        ('essay', 'Эссе'),
        ('feuilleton', 'Фельетон'),
        ('sketch', 'Очерк'),
        ('parable', 'Притча'),
        ('fairy_tale', 'Сказка'),
        ('myth', 'Миф'),
        ('legend', 'Легенда'),
        ('fable', 'Басня'),

        # Поэзия
        ('poem', 'Стихотворение'),
        ('verse', 'Стих'),
        ('ballad', 'Баллада'),
        ('ode', 'Ода'),
        ('elegy', 'Элегия'),
        ('sonnet', 'Сонет'),
        ('epigram', 'Эпиграмма'),
        ('haiku', 'Хайку'),
        ('lyrics', 'Лирика'),
        ('epic_poem', 'Поэма'),
        ('rhyme', 'Рифмовка'),

        # Драматургия
        ('play', 'Пьеса'),
        ('tragedy', 'Трагедия'),
        ('comedy', 'Комедия'),
        ('drama', 'Драма'),
        ('tragicomedy', 'Трагикомедия'),
        ('monologue', 'Монолог'),
        ('skit', 'Сценка'),
        ('script', 'Сценарий'),

        # Публицистика и документалистика
        ('article', 'Статья'),
        ('reportage', 'Репортаж'),
        ('interview', 'Интервью'),
        ('review', 'Рецензия'),
        ('critique', 'Критика'),
        ('column', 'Колонка'),
        ('public_letter', 'Публичное письмо'),
        ('memoirs', 'Мемуары'),
        ('biography', 'Биография'),
        ('autobiography', 'Автобиография'),
        ('diary', 'Дневник'),
        ('letter', 'Письмо'),
        ('speech', 'Речь'),

        # Научные и учебные
        ('scientific_article', 'Научная статья'),
        ('monograph', 'Монография'),
        ('textbook', 'Учебник'),
        ('tutorial', 'Учебное пособие'),
        ('methodical', 'Методичка'),
        ('thesis', 'Диссертация'),
        ('abstract', 'Тезисы'),
        ('lecture', 'Лекция'),
        ('research', 'Исследование'),
        ('dictionary_entry', 'Словарная статья'),
        ('encyclopedia', 'Энциклопедическая статья'),
        ('commentary', 'Комментарий'),

        # Детская литература
        ('children_poem', 'Детское стихотворение'),
        ('lullaby', 'Колыбельная'),
        ('nursery_rhyme', 'Потешка'),
        ('pestushka', 'Пестушка'),
        ('counting_rhyme', 'Считалка'),
        ('tongue_twister', 'Скороговорка'),
        ('riddle', 'Загадка'),
        ('bedtime_story', 'Сказка на ночь'),
        ('educational_story', 'Познавательный рассказ'),

        # Фольклор
        ('folk_tale', 'Народная сказка'),
        ('epic', 'Былина'),
        ('historical_song', 'Историческая песня'),
        ('ritual_poetry', 'Обрядовая поэзия'),
        ('proverb', 'Пословица'),
        ('saying', 'Поговорка'),
        ('chant', 'Закличка'),
        ('folklore', 'Фольклор'),

        # Религиозные тексты
        ('prayer', 'Молитва'),
        ('sermon', 'Проповедь'),
        ('parable_religious', 'Притча религиозная'),
        ('hagiography', 'Житие'),
        ('psalm', 'Псалом'),
        ('canon', 'Канон'),

        # Эпистолярный жанр
        ('epistle', 'Послание'),
        ('open_letter', 'Открытое письмо'),
        ('dedication', 'Посвящение'),
        ('epigraph', 'Эпиграф'),

        # Малые формы
        ('aphorism', 'Афоризм'),
        ('quote', 'Цитата'),
        ('maxim', 'Максима'),
        ('thought', 'Мысль'),
        ('reflection', 'Размышление'),
        ('note', 'Заметка'),
        ('fragment', 'Фрагмент'),
        ('excerpt', 'Отрывок'),

        # Специальные жанры
        ('prologue', 'Пролог'),
        ('epilogue', 'Эпилог'),
        ('foreword', 'Предисловие'),
        ('afterword', 'Послесловие'),
        ('introduction', 'Введение'),
        ('conclusion', 'Заключение'),
        ('appendix', 'Приложение'),
        ('glossary', 'Глоссарий'),

        ('chapter', 'Глава'),
        ('part', 'Часть'),
        ('volume', 'Том'),
        ('section', 'Раздел'),

        # Другое
        ('other', 'Другое'),
        ('mixed', 'Смешанный жанр'),
        ('unknown', 'Не определено'),
    ]

    title = models.CharField('Название произведения', max_length=300)
    original_title = models.CharField('Оригинальное название', max_length=300, blank=True, null=True)
    work_type = models.CharField('Тип произведения', max_length=50, choices=WORK_TYPE_CHOICES, default='fairy_tale')
    first_page = models.IntegerField('Страница начала', null=True, blank=True)
    last_page = models.IntegerField('Страница конца', null=True, blank=True)
    description = models.TextField('Краткое содержание', blank=True, null=True)
    publication_year = models.IntegerField('Год первой публикации', null=True, blank=True)

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='works', verbose_name='Сборник')
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='works',
                               verbose_name='Автор произведения')

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['book', 'first_page', 'title']

    def __str__(self):
        return f"{self.title} - {self.book.title}"

    @property
    def page_range(self):
        if self.first_page and self.last_page:
            return f"Стр. {self.first_page}-{self.last_page}"
        elif self.first_page:
            return f"Стр. {self.first_page}"
        return "Страницы не указаны"

    @property
    def get_work_type_group(self):
        """Возвращает группу жанра произведения"""
        groups = {
            'Художественная проза': ['novel', 'story', 'novella', 'short_story', 'essay', 'feuilleton', 'sketch',
                                     'parable', 'fairy_tale', 'myth', 'legend', 'fable'],
            'Поэзия': ['poem', 'verse', 'ballad', 'ode', 'elegy', 'sonnet', 'epigram', 'haiku', 'lyrics', 'epic_poem',
                       'rhyme'],
            'Драматургия': ['play', 'tragedy', 'comedy', 'drama', 'tragicomedy', 'monologue', 'skit', 'script'],
            'Публицистика': ['article', 'reportage', 'interview', 'review', 'critique', 'column', 'public_letter',
                             'memoirs', 'biography', 'autobiography', 'diary', 'letter', 'speech'],
            'Научные': ['scientific_article', 'monograph', 'textbook', 'tutorial', 'methodical', 'thesis', 'abstract',
                        'lecture', 'research', 'dictionary_entry', 'encyclopedia', 'commentary'],
            'Детская литература': ['children_poem', 'lullaby', 'nursery_rhyme', 'pestushka', 'counting_rhyme',
                                   'tongue_twister', 'riddle', 'bedtime_story', 'educational_story'],
            'Фольклор': ['folk_tale', 'epic', 'historical_song', 'ritual_poetry', 'proverb', 'saying', 'chant',
                         'folklore'],
            'Религиозные': ['prayer', 'sermon', 'parable_religious', 'hagiography', 'psalm', 'canon'],
            'Эпистолярный': ['epistle', 'open_letter', 'dedication', 'epigraph'],
            'Малые формы': ['aphorism', 'quote', 'maxim', 'thought', 'reflection', 'note', 'fragment', 'excerpt'],
            'Структурные': ['chapter', 'part', 'volume', 'section', 'prologue', 'epilogue', 'foreword', 'afterword',
                            'introduction', 'conclusion', 'appendix', 'glossary'],
        }

        for group, types in groups.items():
            if self.work_type in types:
                return group
        return 'Другое'