FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код
COPY . .

# Создаём директорию для статики
RUN mkdir -p /app/staticfiles

# ❌ УБИРАЕМ collectstatic из сборки
# RUN python manage.py collectstatic --noinput

EXPOSE 8000

# ✅ Запускаем миграции, собираем статику и запускаем GUNICORN (не runserver!)
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn nn_project.wsgi:application --bind 0.0.0.0:8000"]