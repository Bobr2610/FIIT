# ExchangeDashboard

## Команда
1. **Белянский Кирилл** : Main Frontend Developer
2. **Литвак Александр** : ...
3. **Сальманов Эльдар** : Main Backend Developer
4. **Седов Михаил**     : Leader
---

# Setup

## 1. Установка внешних зависимостей

Для запуска проекта требуется Python, Poetry.

### Windows
```shell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

### Mac OS & Linux
```shell
curl -sSL https://install.python-poetry.org | python3 -
```

#### Замечание: после установки нужно перезапустить консоль!

## 2. Клонирование репозитория
```shell
git clone https://github.com/Bobr2610/Python_team
```

## 3. Переход в папку проекта
```shell
cd Python_team
```

## 4. Настройка Poetry
```shell
poetry config virtualenvs.in-project true
```

## 5. Установка внутренних зависимостей
```shell
poetry install
```

---

# Run

## Запуск проекта
```shell
poetry run python manage.py runserver
```

---
