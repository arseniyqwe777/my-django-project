# 📚 BookBridge

> Современная библиотечная система на Django с поиском, авторизацией и админ-панелью.

[![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.1-green?logo=django)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue?logo=postgresql)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-✓-blue?logo=docker)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

🔗 **Живой демо-сайт:** [bookbridge.ru](https://arseniyqwe777-my-django-project-d6f4.twc1.net)

---

## О проекте

**BookBridge** — это веб-приложение для каталогизации книг, авторов и произведений. Проект создан как портфолио для Junior Python-разработчика и демонстрирует навыки работы с Django, PostgreSQL, Docker и деплоем в облаке.

### Возможности

- 🔐 **Авторизация** — регистрация, вход, выход
- 📚 **Crud** — создание, чтение, обновление, удаление книг, авторов, произведений
- 🔍 **Поиск** — по названию, автору, инвентарному номеру
- 🧩 **Расширенный поиск** — фильтрация по типу произведения и году публикации
- 🖼️ **Обложки** — загрузка изображений для книг
- 👑 **Админ-панель** — управление контентом
- ⭐ **Избранное** — добавление книг в избранное
- 📤 **Экспорт** — выгрузка данных в csv

---

## Технологический стек

| Компонент | Технология |
|-----------|------------|
| **Язык** | Python 3.11 |
| **Фреймворк** | Django 5.1 |
| **База данных** | PostgreSQL 16 |
| **Сервер** | Gunicorn |
| **Статика** | Whitenoise |
| **Контейнеризация** | Docker |
| **Фронтенд** | Bootstrap 5, Html5, Css3 |
| **Деплой** | Timeweb Cloud |
| **Версионирование** | Git, GitHub |

---

## Быстрый старт

```bash
# Клонировать репозиторий
git clone https://github.com/arseniyqwe777/my-django-project.git
cd my-django-project

# Создать виртуальное окружение
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Установить зависимости
pip install -r requirements.txt

# Применить миграции
python manage.py migrate

# Создать суперпользователя
python manage.py createsuperuser

# Запустить сервер
python manage.py runserver
```

---

## Скриншоты

<div align="center">
  <img src="screenshots/screenshot-main.png" width="45%" alt="Главная страница">
  <img src="screenshots/screenshot-search.png" width="45%" alt="Поиск">
</div>

<div align="center">
  <img src="screenshots/screenshot-book.png" width="45%" alt="Страница книги">
  <img src="screenshots/screenshot-author.png" width="45%" alt="Страница автора">
</div>

---

## Структура проекта

```
nn_project/
├── app/                    # Основное приложение
│   ├── models.py           # Модели данных
│   ├── views.py            # Контроллеры
│   ├── urls.py             # Маршруты
│   ├── forms.py            # Формы
│   └── admin.py            # Настройки админки
├── nn_project/             # Настройки проекта
├── screenshots/            # Скриншоты для readme
├── staticfiles/            # Собранная статика
├── Dockerfile              # Docker-сборка
├── requirements.txt        # Зависимости
└── manage.py               # Управляющий скрипт
```

---

## Что дальше?

- [ ] Rest Api (Django Rest Framework)
- [ ] Автотесты
- [ ] Кэширование (Redis)
- [ ] Telegram-бот

---

## Автор

**Арсений**  
Студент специальности 09.02.07 «Информационные системы и программирование»

[![GitHub](https://img.shields.io/badge/GitHub-arseniyqwe777-181717?logo=github)](https://github.com/arseniyqwe777)
[![Telegram](https://img.shields.io/badge/Telegram-@arseniy-26A5E4?logo=telegram)](https://t.me/arseniy)

---

⭐ **Если проект был полезен, поставьте звёздочку на GitHub!**