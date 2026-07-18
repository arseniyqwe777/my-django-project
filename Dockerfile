FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Удаляем старую БД и создаём новую
RUN rm -f db.sqlite3
RUN python manage.py migrate --noinput
RUN python manage.py collectstatic --noinput

EXPOSE 80

CMD ["gunicorn", "nn_project.wsgi:application", "--bind", "0.0.0.0:80"]