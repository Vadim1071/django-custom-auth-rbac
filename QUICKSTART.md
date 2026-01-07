# Быстрый старт

## Шаги для запуска проекта

### 1. Убедитесь, что PostgreSQL установлен и запущен

### 2. Создайте базу данных:
```sql
CREATE DATABASE auth_system_db;
```

### 3. Создайте файл `.env` в корне проекта:
```env
DB_NAME=auth_system_db
DB_USER=postgres
DB_PASSWORD=ваш_пароль
DB_HOST=localhost
DB_PORT=5432
```

### 4. Активируйте виртуальное окружение:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 5. Примените миграции:
```bash
python manage.py migrate
```

### 6. Заполните тестовыми данными:
```bash
python manage.py init_data
```

### 7. Запустите сервер:
```bash
python manage.py runserver
```

## Тестирование API

### Пример: Регистрация и получение токена

```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "first_name": "Тест",
    "last_name": "Тестов",
    "password": "test123456",
    "password_confirm": "test123456"
  }'
```

### Пример: Вход в систему

```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "admin123"
  }'
```

### Пример: Получение списка проектов (требует токен)

```bash
curl -X GET http://localhost:8000/api/projects/ \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Тестовые пользователи

После выполнения `python manage.py init_data`:

- **admin@example.com** / `admin123` - администратор
- **manager@example.com** / `manager123` - менеджер  
- **user@example.com** / `user123` - обычный пользователь

Подробная документация в [README.md](README.md)
