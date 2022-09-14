Тестовое задание с использованием DFR\
#Инструкция по запуску:

#Конфигурация проекта
1. pip install -r requirements.txt
2. python manage.py makemigrations
3. python manage.py migrate

#Celery + Redis
4. docker run -d -p 6379:6379 redis
5. celery -A config worker -P solo -l INFO

#Запуск проекта
6. python manage.py runserver