# Проект Foodgram

## Описание проекта Foodgram
Foodgram представляет собой ресурс, позволяющий пользователям публиковать свои **рецепты**, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список **«Избранное»**, а перед походом в магазин скачивать сводный **список продуктов**, необходимых для приготовления одного или нескольких выбранных блюд.

У каждого рецепта есть теги из списка предустановленных (например, «завтрак», «обед» или «ужин»). В проекте реализована удобная система фильтрации рецептов по тегам.

## Технологии:
- Pyhton 
- Django 
- Djoser 
- DRF
- PostgreSQL
- NGINX
- Gunicorn
- Docker

## Пользовательские роли
- **Гость (неавторизованный пользователь)** — может:
    - создать аккаунт, 
    - просматривать рецепты на главной странице, 
    - просматривать отдельные страницы рецептов и пользователей,
    - фильтровать рецепты по тегам.
- **Авторизованный пользователь** — может, выполнять действия доступные **Гостю**, и дополнительно может: 
    - входить в систему под своим логином и паролем, выходить из системы, менять свой пароль, 
    - создавать/редактировать/удалять собственные рецепты, работать с персональным списком избранного: добавлять в него рецепты или удалять их, просматривать свою страницу избранных рецептов, 
    - работать с персональным списком покупок: добавлять/удалять любые рецепты, выгружать файл с количеством необходимых ингредиентов для рецептов из списка покупок, 
    - подписываться на публикации авторов рецептов и отменять подписку, просматривать свою страницу подписок.
- **Администратор** — обладает всеми правами авторизованного пользователя, плюс к этому он может:
    - изменять пароль любого пользователя,
    - создавать/блокировать/удалять аккаунты пользователей,
    - редактировать/удалять любые рецепты, 
    - добавлять/удалять/редактировать ингредиенты.

## Как развернуть проект на сервере:
Склонируйте проект из репозитория:

```
$ git clone git@github.com:vvgornostaeva/foodgram-project-react.git
```
Установите соединение с сервером:
```
ssh username@server_address
```
Обновите индекс пакетов APT и обновите установленные в системе пакеты и установите обновления безопасности:
```
sudo apt update
sudo apt upgrade -y
```
Установите Docker и Docker-compose:
```
sudo apt install docker.io
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

Проверьте корректность установки Docker-compose:
```
sudo  docker-compose --version
```
Скопируйте из папки ..infra/ файлы `docker-compose.yml` и `nginx.conf` из вашего проекта на сервер предварительно заменив в файле nginx.conf в строке `server_name`  IP вашей виртуальной машины (сервера):
```
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yaml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```

На сервере создайте файл .env и заполните переменные окружения
```
touch .env
```
```python
Шаблон для заполнения файла ".env":
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY='Здесь указать секретный ключ'
ALLOWED_HOSTS='Здесь указать имя или IP хоста' (Для локального запуска - 127.0.0.1)
``` 

Установите и активируйте виртуальное окружение (для Windows):

```sh
python -m venv venv 
source venv/Scripts/activate
python -m pip install --upgrade pip
``` 

Запустите приложение в контейнерах:

```sh
sudo docker-compose up -d --build
```
Последовательно выполлните следующие команды:
```
sudo docker-compose exec backend python manage.py migrate
sudo docker compose exec backend python manage.py collectstatic
sudo docker compose exec backend cp -r static/. ..static/
sudo docker compose exec backend python manage.py createsuperuser
sudo docker compose exec backend python manage.py import_csv
```
### Особенности заполнения данными:

- Для того чтобы иметь возможность добавлять рецепты, сперва добавьте теги для для рецептов через админ-панель проекта, т.к. это поле является обязательным для сохранения рецепта и добавляется только админом.

### Тестовые пользователи
Логин: ```vikaadmin``` (суперюзер)  
Email: ```vvgornostaeva@mail.ru``  
Пароль: ```123456```  

Логин: ```vasilinapupkina```  
Email: ```pupkina@mail.ru```  
Пароль: ```qwerty12345666```  

Логин: ```vasya.pupkin```  
Email: ```vpupkin@yandex.ru```  
Пароль: ```qwerty12345666```

### Ссылка на сайт, развернутый на сервере:
##### [foodgram](https://recipefoodgram.ddns.net/recipes)
### Автор проекта:
##### [Виктория Горностаева](https://github.com/vvgornostaeva)
