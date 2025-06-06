Pet Blog
Описание проекта
Pet Blog — это веб-приложение на Django, предназначенное для управления списком питомцев. 
Пользователи могут добавлять, редактировать, удалять и просматривать информацию о питомцах, включая их родословную и отзывы. 
Проект поддерживает:

Разделение питомцев на активных и неактивных с пагинацией для каждого списка.
Фильтрацию по кличке, виду, возрасту, владельцу и дате создания.
Роли пользователей: администраторы, модераторы и обычные пользователи с разными уровнями доступа.
Отправку email-уведомлений (например, при достижении 100 просмотров питомца).
Мультиязычность (i18n) и поддержку медиафайлов.

Требования

Python 3.9+
Django 4.2+
PostgreSQL (рекомендуется) или SQLite
Зависимости, указанные в requirements.txt

Установка и запуск
1. Клонирование репозитория
Склонируйте репозиторий на свой компьютер:
git clone https://github.com/your-username/pet-blog.git
cd pet-blog

2. Настройка виртуального окружения
Создайте и активируйте виртуальное окружение:
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate

3. Установка зависимостей
Установите необходимые пакеты:
pip install -r requirements.txt

Пример requirements.txt (создайте, если отсутствует):
django==4.2.11
psycopg2-binary==2.9.9
django-bootstrap5==24.2
django-filter==24.2

4. Настройка базы данных
Настройте базу данных в config/settings.py. Пример для SQLite:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

Для PostgreSQL установите psycopg2 и настройте:
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'petblog_db',
        'USER': 'your_user',
        'PASSWORD': 'your_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

Примените миграции:
python manage.py makemigrations
python manage.py migrate

5. Создание суперпользователя
Создайте администратора для доступа к админке:
python manage.py createsuperuser

6. Настройка email (опционально)
Настройте email в config/settings.py для отправки уведомлений:
EMAIL_HOST = 'smtp.your-email-provider.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'your-email@example.com'

7. Запуск проекта
Запустите сервер разработки:
python manage.py runserver

Откройте браузер и перейдите по адресу: http://127.0.0.1:8000/ru/blog/.
Админка доступна по адресу: http://127.0.0.1:8000/admin/.
Использование

Список питомцев: На главной странице (/ru/blog/) отображаются активные и неактивные питомцы с пагинацией. Используйте фильтры для поиска.
Добавление питомца: Авторизованные пользователи могут добавить питомца через кнопку "Добавить питомца".
Роли:
Обычные пользователи видят только активных питомцев.
Администраторы и модераторы могут видеть и управлять неактивными питомцами, изменять их статус.


Уведомления: При достижении 100 просмотров питомца владельцу отправляется email.

Структура проекта

blog/: Приложение для управления питомцами.
models.py: Модели Pet, Pedigree, Review.
views.py: Представления для списка, деталей, создания, обновления и удаления питомцев.
templates/blog/: Шаблоны (pet_list.html, pet_detail.html и др.).


users/: Приложение для управления пользователями (регистрация, профиль, список пользователей).
config/: Основные настройки проекта (settings.py, urls.py).

Дополнительно

Для локализации убедитесь, что установлены языковые пакеты и сгенерированы файлы перевода:python manage.py compilemessages


Для работы с медиафайлами настройте MEDIA_URL и MEDIA_ROOT в settings.py.



Создано: 28 мая 2025 года.
