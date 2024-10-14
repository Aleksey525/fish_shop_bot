# Бот для продажи рыбы через телеграмм
Бот, интегрированный в CMS магазина по продажи рыбы.


### Как установить

Python3.11 должен быть уже установлен. Затем используйте `pip` (или `pip3`, есть конфликт с Python2) для установки зависимостей:

```

pip install -r requirements.txt

```

Создать аккаунт [Redis](https://redis.io/). После получить адрес, порт и пароль от базы данных. 

CMS [Starapi](https://github.com/strapi/strapi?tab=readme-ov-file#-installation) написана на `JavaScript`, поэтому нужно 
установить [NodeJS](https://nodejs.org/en/) и `npm` локально.
```
nodejs --version
v18.19.1
npm --version
9.2.0
```
Версия `NodeJs` указана для `Starapi 5.0.2`. Версию `npm` можно установить любую. 
Подробнее о совместимости версий читайте по 
[ссылке](https://github.com/strapi/strapi?tab=readme-ov-file#-installation)

Затем нужно создать и развернуть проект `Starapi` локально, см. 
[документацию](https://github.com/strapi/strapi?tab=readme-ov-file#-installation)

После запуска CMS создать модель товара `Product` с полями `title` - type:Text, `description` - type:Text,
`picture` - type:Media, `price` - type:Number. После заполнить данными и поставить статус каждого продукта `Published`.



### Примеры запуска бота

```
python main.py 
```

### Переменные окружения

Часть настроек проекта берётся из переменных окружения. Чтобы их определить, создайте файл `.env` в корневом каталоге проекта и 
запишите туда данные в таком формате: `ПЕРЕМЕННАЯ=значение`.

Доступны 6 переменных:
- `TG_BOT_TOKEN` — API-токен телеграм-бота 
- `STRAPI_TOKEN` — API-токен `CMS Strapi`
- `TG_LOGGER_BOT_TOKEN` — API-токен телеграм-бота для мониторинга
- `REDIS_HOST` — адрес базы данных [Redis](https://redis.io/)
- `REDIS_PASSWORD` — пароль от базы данных [Redis](https://redis.io/)
- `REDIS_PORT` — порт базы данных [Redis](https://redis.io/)


## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman.org](https://dvmn.org).