# Лабораторная №8 - экосистемы Python

Дерябин Илья Игоревич, группа 221341, вариант 5, лабораторная №8

Утилита `mtp-title` принимает тему черновика статьи и предлагает один
заголовок. Внешняя модель - Qwen3-14B на Wikimedia Lift Wing.

| Уровень | № | Задание | Где смотреть |
| --- | --- | --- | --- |
| Средний | 5 | Структура проекта с папкой src | [src/lab8](src/lab8) |
| Средний | 7 | Использовать logging | [cli.py](src/lab8/cli.py) и [liftwing.py](src/lab8/liftwing.py) |
| Средний | 1 | Установить Poetry и создать проект | [pyproject.toml](pyproject.toml) и [poetry.lock](poetry.lock) |
| Повышенный | 6 | Настроить Docker | [Dockerfile](Dockerfile) и [.dockerignore](.dockerignore) |
| Повышенный | 8 | Интегрировать внешний ИИ API | [liftwing.py](src/lab8/liftwing.py), функция `suggest_title` |

## Запуск из PowerShell

Нужен Python 3.11 или новее. Команды выполняются из корня репозитория.

~~~powershell
py -m pip install --user poetry==2.2.1
poetry install
$env:PYTHONUTF8 = '1'
poetry run mtp-title 'Как солнечные часы показывают время'
~~~

Если PowerShell не находит `poetry`, добавь папку скриптов в PATH
текущего терминала и повтори запуск.

~~~powershell
$scriptsDir = py -c "import sysconfig; print(sysconfig.get_path('scripts', 'nt_user'))"
$env:Path = "$scriptsDir;$env:Path"
~~~

Возможный результат - «Как работают солнечные часы». Модель может предложить
другую формулировку. Заголовок выводится в stdout, журнал запроса - в stderr.
Подробные данные запроса и ответа в журнал не пишутся.

Тема из 1-300 символов отправляется в публичный API Wikimedia. Для запроса
нужен интернет. Ключ не требуется. При сетевой ошибке или ограничении
частоты утилита выводит причину и завершается с кодом 1. Неверный аргумент
даёт код 2. [Документация Lift Wing](https://wikitech.wikimedia.org/wiki/Machine_Learning/LiftWing/Large_Language_Models#API_Usage)

## Docker

~~~powershell
docker build -t mtp-lab8 .
docker run --rm mtp-lab8 --help
docker run --rm mtp-lab8 'Как солнечные часы показывают время'
~~~

На этапе сборки Poetry устанавливает зависимости из `poetry.lock` и
собирает wheel. В итоговом образе остаётся только приложение с его зависимостями.

## Проверка

~~~powershell
poetry check --lock --strict
poetry run flake8 src tests
poetry run pytest -q
~~~

В тестах HTTP-ответы подменяются через `httpx.MockTransport`. Проверяются
формат запроса, успешный ответ, ошибки сети и HTTP, некорректная тема и коды
выхода CLI. Живой запрос проверен отдельно.
[Отчёт о проверке](docs/checks.md) ·
[GitHub Actions](https://github.com/EnroXD1/mtp-lab8-variant5/actions)
