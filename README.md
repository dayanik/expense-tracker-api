# expense-tracker-api
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
expense tracker api with registration and authorization. idea from [roadmap.sh](https://roadmap.sh/projects/expense-tracker-api)
---
## 🎯 Возможности

- регистрация пользователей
- аутентификация и выдача токена
- crud задач
- авторизация только аутентифицированных пользователей
- обработка ошибок и безопасность
- валидация данных
- пагинация и фильтрация данных
- фильтрация списка покупок
	- последняя неделя
	- последний месяц
	- последние 3 месяца
	- кастомный период: старт-конец

---
## 🛠 Установка и запуск

1. Клонируй репозиторий и перейди в директорию проекта

```bash
git clone https://github.com/dayanik/expense-tracker-api.git
cd expense-tracker-api
```

2. В этом проекте используется sqlite3 асинхронная версия

3. Скопируй файл конфигурационных переменных и перезапиши их значения

```bash
cp example.env .env
```

4. Запусти проект с помощью Docker-compose:

```bash
docker-compose up -d --build
````

---
## 🔄 Примеры API

| Метод  | Путь                                  | Описание                                         |
| ------ | ------------------------------------- | ------------------------------------------------ |
| POST   | `/register`                           | Зарегестрироваться/создать пользователя          |
| POST   | `/login`                              | Залогиниться/получить токен                      |
| POST   | `/expenses`                           | Создать покупку                                  |
| GET    | `/expenses/{expense_id}`              | Получение покупки по id                          |
| PUT    | `/expenses/{expense_id}`              | Изменить покупку                                 |
| GET    | `/expenses?limit=10&page=2`           | Получить список покупок с пагинацией             |
| GET    | `/expenses?period=week/month/quarter` | Список покупок последней недели/месяца/3 месяцев |
| DELETE | `/expenses/{expense_id}`              | Удалить покупку по id                            |

**Пример ответа:**

```json
{
  "data": [
    {
      "id": 1,
      "title": "Buy groceries",
      "description": "Buy milk, eggs, bread"
    },
    {
      "id": 2,
      "title": "Pay bills",
      "description": "Pay electricity and water bills"
    }
  ],
  "page": 1,
  "limit": 10,
  "total": 2
}
```

---

## ✅ Проверка и тесты

*(если ты добавишь тесты — укажи здесь как их запускать: jest, mocha и т.д.)*

```bash
test
```

---
## 📈 Стек технологий

* FastAPI[standard]
* AIOSQLite3
* ORM SqlAlchemy[asyncio]
* Docker
* PyJWT
* pwdlib[argon]
---
## 📄 Лицензия

Этот проект лицензирован под [MIT License](LICENSE).

---
## ✍🏼 Контакты / Благодарности

Если хочешь связаться или внести вклад — открывай issue или pull request.
Большое спасибо за интерес к проекту!