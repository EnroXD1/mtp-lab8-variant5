"""Проверки кодов завершения и вывода команды."""

import logging

import pytest

from lab8.cli import main
from lab8.liftwing import LiftWingError


def test_success_outputs_title(monkeypatch, capsys):
    monkeypatch.setattr("lab8.cli.suggest_title", lambda *_: "Солнечные часы")
    assert main(["История гномонов"]) == 0
    assert capsys.readouterr().out.strip() == "Солнечные часы"


def test_service_failure_returns_one(monkeypatch, caplog, capsys):
    def fail(*_):
        raise LiftWingError("Lift Wing вернул HTTP 503.")

    monkeypatch.setattr("lab8.cli.suggest_title", fail)
    assert main(["Тема"]) == 1
    assert not capsys.readouterr().out
    assert caplog.records[-1].levelno == logging.ERROR
    assert "HTTP 503" in caplog.text


def test_invalid_input_returns_two(capsys):
    with pytest.raises(SystemExit) as exit_info:
        main(["  "])
    assert exit_info.value.code == 2
    assert "Длина темы" in capsys.readouterr().err
