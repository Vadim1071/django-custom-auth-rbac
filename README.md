# Django Custom Auth & RBAC

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Django](https://img.shields.io/badge/Django-6.0-green)
![DRF](https://img.shields.io/badge/DRF-3.15-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-blue)


# Система аутентификации и авторизации на Django REST Framework

Собственная система аутентификации и авторизации с разграничением прав доступа на основе ролей (RBAC).

## Архитектура системы

### Модель доступа: RBAC (Role-Based Access Control)

Система использует модель **RBAC** с расширенными возможностями:
- **Пользователи** имеют **Роли**
- **Роли** содержат **Разрешения**
- **Разрешения** определяют доступ к **Ресурсам** и **Действиям**

### Схема базы данных

#### 1. User (Пользователь)
- `id` - первичный ключ
- `email` - уникальный email
- `password` - хешированный пароль
- `first_name` - имя
- `last_name` - фамилия
- `middle_name` - отчество (опционально)
- `is_active` - флаг активности (для мягкого удаления)
- `created_at` - дата создания
- `updated_at` - дата обновления

#### 2. Role (Роль)
- `id` - первичный ключ
- `name` - уникальное название роли
- `description` - описание роли
- `created_at` - дата создания

#### 3. Permission (Разрешение)
- `id` - первичный ключ
- `resource_type` - тип ресурса (например: "project", "document")
- `action` - действие (например: "read", "write", "delete")
- `description` - описание разрешения
- `created_at` - дата создания

#### 4. RolePermission (Связь роли и разрешения)
- `id` - первичный ключ
- `role_id` - внешний ключ на Role
- `permission_id` - внешний ключ на Permission
- `created_at` - дата создания

#### 5. UserRole (Связь пользователя и роли)
- `id` - первичный ключ
- `user_id` - внешний ключ на User
- `role_id` - внешний ключ на Role
- `assigned_at` - дата назначения

#### 6. AccessToken (Токен доступа)
- `id` - первичный ключ
- `user_id` - внешний ключ на User
- `token` - уникальный токен
- `expires_at` - дата истечения
- `created_at` - дата создания
- `last_used_at` - дата последнего использования

### Логика работы

#### Аутентификация
1. Пользователь регистрируется или логинится
2. Система создает токен доступа (срок действия 30 дней)
3. Токен возвращается клиенту
4. Клиент отправляет токен в заголовке `Authorization: Bearer <token>`

#### Авторизация
1. Middleware извлекает токен из запроса
2. Проверяет валидность токена и получает пользователя
3. Определяет, какие роли имеет пользователь
4. Проверяет, есть ли у ролей пользователя разрешение на запрашиваемый ресурс и действие
5. Если разрешение есть - доступ разрешен, иначе - 403 Forbidden
6. Если пользователь не определен - 401 Unauthorized

### Роли по умолчанию

1. **admin** - полный доступ ко всем ресурсам
   - Все разрешения на все ресурсы

2. **manager** - управление проектами и чтение документов
   - `project:read`, `project:write`
   - `document:read`

3. **user** - только чтение
   - `project:read`
   - `document:read`

## Установка и настройка

### Требования
- Python 3.8+
- PostgreSQL 12+
- pip

### Шаги установки

1. **Клонируйте репозиторий или создайте проект**

2. **Создайте виртуальное окружение:**
```bash
python -m venv venv
```

3. **Активируйте виртуальное окружение:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

5. **Создайте базу данных PostgreSQL:**
```sql
CREATE DATABASE auth_system_db;
CREATE USER postgres WITH PASSWORD 'postgres';
GRANT ALL PRIVILEGES ON DATABASE auth_system_db TO postgres;
```

6. **Настройте переменные окружения:**
Создайте файл `.env` в корне проекта:
```env
DB_NAME=auth_system_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key-here
```

7. **Примените миграции:**
```bash
python manage.py makemigrations
python manage.py migrate
```

8. **Заполните тестовыми данными:**
```bash
python manage.py init_data
```

9. **Запустите сервер:**
```bash
python manage.py runserver
```

## API Endpoints

### Аутентификация

#### Регистрация
```http
POST /api/auth/register/
Content-Type: application/json

{
    "email": "user@example.com",
    "first_name": "Иван",
    "last_name": "Иванов",
    "middle_name": "Иванович",
    "password": "securepassword123",
    "password_confirm": "securepassword123"
}
```
<img width="1360" height="768" alt="image" src="https://github.com/user-attachments/assets/4f6369ef-e50a-487a-bb66-fd5a29886da6" />

#### Вход в систему
```http
POST /api/auth/login/
Content-Type: application/json

{
    "email": "user@example.com",
    "password": "securepassword123"
}
```

**Ответ:**
```json
{
    "message": "Успешный вход в систему",
    "token": "your-access-token-here",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "first_name": "Иван",
        "last_name": "Иванов",
        "middle_name": "Иванович",
        "full_name": "Иванов Иван Иванович",
        "roles": ["user"]
    }
}
```

#### Выход из системы
```http
POST /api/auth/logout/
Authorization: Bearer <token>
```

#### Получение информации о текущем пользователе
```http
GET /api/auth/me/
Authorization: Bearer <token>
```

#### Обновление профиля
```http
PUT /api/auth/update_me/
Authorization: Bearer <token>
Content-Type: application/json

{
    "first_name": "Новое имя",
    "last_name": "Новая фамилия",
    "middle_name": "Новое отчество"
}
```

#### Удаление аккаунта (мягкое)
```http
DELETE /api/auth/delete_me/
Authorization: Bearer <token>
```

### Управление правами (только для администратора)

#### Получение списка ролей
```http
GET /api/roles/
Authorization: Bearer <admin-token>
```

#### Создание роли
```http
POST /api/roles/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
    "name": "new_role",
    "description": "Описание новой роли"
}
```

#### Добавление разрешения к роли
```http
POST /api/roles/{role_id}/add_permission/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
    "permission_id": 1
}
```

#### Удаление разрешения из роли
```http
DELETE /api/roles/{role_id}/remove_permission/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
    "permission_id": 1
}
```

#### Получение списка разрешений
```http
GET /api/permissions/
Authorization: Bearer <admin-token>
```

#### Назначение роли пользователю
```http
POST /api/user-roles/
Authorization: Bearer <admin-token>
Content-Type: application/json

{
    "user": 1,
    "role": 2
}
```

### Mock-ресурсы (для демонстрации)

#### Получение списка проектов
```http
GET /api/projects/
Authorization: Bearer <token>
```
**Требует разрешение:** `project:read`

#### Создание проекта
```http
POST /api/projects/
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "Новый проект",
    "description": "Описание проекта"
}
```
**Требует разрешение:** `project:write`

#### Получение списка документов
```http
GET /api/documents/
Authorization: Bearer <token>
```
**Требует разрешение:** `document:read`

#### Создание документа
```http
POST /api/documents/
Authorization: Bearer <token>
Content-Type: application/json

{
    "title": "Новый документ",
    "content": "Содержимое документа"
}
```
**Требует разрешение:** `document:write`

## Обработка ошибок

### 401 Unauthorized
Возвращается, когда:
- Токен не предоставлен
- Токен невалиден
- Токен истек
- Пользователь деактивирован

**Пример ответа:**
```json
{
    "error": "Unauthorized",
    "message": "Требуется аутентификация",
    "detail": "Неверный токен доступа"
}
```

### 403 Forbidden
Возвращается, когда:
- Пользователь авторизован, но не имеет доступа к запрашиваемому ресурсу

**Пример ответа:**
```json
{
    "error": "Forbidden",
    "message": "Доступ запрещен",
    "detail": "У вас нет доступа к project:write"
}
```

## Тестовые пользователи

После выполнения команды `python manage.py init_data` создаются следующие тестовые пользователи:

- **admin@example.com** / `admin123` - администратор (полный доступ)
- **manager@example.com** / `manager123` - менеджер (управление проектами, чтение документов)
- **user@example.com** / `user123` - пользователь (только чтение)

## Примеры использования

### Пример 1: Регистрация и получение списка проектов

```bash
# 1. Регистрация
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "first_name": "Новый",
    "last_name": "Пользователь",
    "password": "password123",
    "password_confirm": "password123"
  }'

# 2. Получение токена (из ответа выше)
TOKEN="your-token-here"

# 3. Получение списка проектов
curl -X GET http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer $TOKEN"
```

### Пример 2: Вход администратора и создание роли

```bash
# 1. Вход
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'

# 2. Получение токена
ADMIN_TOKEN="admin-token-here"

# 3. Создание новой роли
curl -X POST http://localhost:8000/api/roles/ \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "editor",
    "description": "Редактор - может редактировать проекты и документы"
  }'
```

## Структура проекта

```
auth_system/
├── config/              # Настройки Django проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── auth_app/           # Приложение аутентификации
│   ├── models.py       # Модели БД
│   ├── views.py        # API представления
│   ├── serializers.py  # Сериализаторы
│   ├── authentication.py  # Кастомная аутентификация
│   ├── permissions.py  # Система разрешений
│   ├── exceptions.py   # Обработка исключений
│   ├── urls.py         # URL маршруты
│   └── management/
│       └── commands/
│           └── init_data.py  # Команда для тестовых данных
├── venv/               # Виртуальное окружение
├── .env               # Переменные окружения (не в git)
├── requirements.txt   # Зависимости
└── README.md         # Документация
```

## Особенности реализации

1. **Собственная система аутентификации** - не использует встроенную систему Django
2. **Кастомные токены** - токены генерируются с помощью `secrets.token_urlsafe()`
3. **Мягкое удаление** - пользователи деактивируются, но остаются в БД
4. **Гибкая система прав** - легко добавлять новые ресурсы и действия
5. **Администратор имеет полный доступ** - автоматически пропускается проверка разрешений

## Разработка

### Запуск тестового сервера
```bash
python manage.py runserver
```

### Создание миграций
```bash
python manage.py makemigrations
```

### Применение миграций
```bash
python manage.py migrate
```

### Создание суперпользователя (опционально, для админ-панели Django)
```bash
python manage.py createsuperuser
```

## Лицензия

Этот проект создан в образовательных целях.
