![alt text](frontend/img/whitelogo.png "FIIT")

# FIIT – Financial Intelligent Investment Tracker

## Команда
1. **Белянский Кирилл** : Lead Frontend Developer
2. **Сальманов Эльдар** : Lead Backend Developer
3. **Седов Михаил**     : Leader, Support Frontend & Backend Developer
---
Для подробностей о работе биржы перейдите на WIKI
---
# Setup

## 1. Установка внешних зависимостей

Для запуска проекта требуется
1. [Docker](https://www.docker.com/)

## 2. Клонирование репозитория
```shell
git clone https://github.com/Bobr2610/FIIT
```

## 3. Переход в папку проекта
```shell
cd FIIT
```

## 4. Настройка файлов окружения
Скопировать файл `config/.env.example` в эту же папку, назвав его `.env`, и заполнить его.

# Build

## Сборка проекта

```shell
docker compose build
```

---

# Run

## Запуск проекта

```shell
docker compose up
```

## Запуск проекта с пересборкой

```shell
docker compose up --build
```
