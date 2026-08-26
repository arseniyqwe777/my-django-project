FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Собираем статику на этапе сборки
RUN python manage.py collectstatic --noinput

EXPOSE 80

# Миграции выполняются при запуске контейнера
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn nn_project.wsgi:application --bind 0.0.0.0:80"]