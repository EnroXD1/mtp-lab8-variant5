# Проверка лабораторной №8

24.11.2026. Windows, Python 3.12, Poetry 2.2.1.
`poetry check --lock --strict` и flake8 прошли.
`poetry run pytest -q` дал 15 успешных проверок.

## Живой запрос

~~~text
$ poetry run mtp-title 'Как солнечные часы показывают время'
INFO Запрос к Wikimedia Lift Wing, модель llm-qwen3-14b
INFO Получен ответ Lift Wing (HTTP 200)
Как работают солнечные часы
~~~

## Docker

В [GitHub Actions](https://github.com/EnroXD1/mtp-lab8-variant5/actions)
образ собирается из Dockerfile. Из образа запускаются `--help`,
`--version` и команда с пустой темой. Последняя должна завершиться с кодом 2.
Эти запуски проходят без сети, отдельно от проверки Wikimedia.
