import os
import re
from typing import Iterator  # добавить типизацию в проект, чтобы проходила утилиту mypy app.py

from flask import Flask, request, Response
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def build_query(f: Iterator, cmd1: str, cmd2: str, value1: str, value2: str) -> Iterator:
    res: Iterator = map(lambda x: x.strip(), f)
    res = apply_cmd(res, cmd1, value1)
    return apply_cmd(res, cmd2, value2)


def apply_cmd(data: Iterator, cmd: str, value: str) -> Iterator:
    if cmd == "filter":  # с помощью функционального программирования (функций filter, map), итераторов/генераторов сконструировать запрос
        return filter(lambda t: value in t, data)
    if cmd == "map":
        idx = int(value)
        return map(lambda t: t.split(" ")[idx], data)
    if cmd == "unique":
        return iter(set(data))
    if cmd == "sort":
        reverse = bool(value == "desc")
        return iter(sorted(data, reverse=reverse))
    if cmd == "limit":
        arg = int(value)
        return sl_limit(data, arg)
    if cmd == "regex":  # добавить команду regex
        regex = re.compile(value)
        return filter(lambda t: regex.search(t), data)
    return data


def sl_limit(data: Iterator, limit: int) -> Iterator:
    i = 0
    for item in data:
        if i < limit:
            yield item
        else:
            break
        i += 1


@app.post("/perform_query")
def perform_query() -> Response:
    try:  # получить параметры query и file_name из request.args, при ошибке вернуть ошибку 400
        file_name = request.form["file_name"]
        cmd1 = request.form["cmd1"]
        cmd2 = request.form["cmd2"]
        value1 = request.form["value1"]
        value2 = request.form["value2"]
    except KeyError:
        raise BadRequest

    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):  # проверить, что файла file_name существует в папке DATA_DIR, при ошибке
        # вернуть ошибку 400
        raise BadRequest(f"{file_name} was not found")

    with open(file_path) as f:
        res = build_query(f, cmd1, cmd2, value1, value2)
        data = '\n'.join(res)
    # вернуть пользователю сформированный результат
    return app.response_class(data, content_type="text/plain")
