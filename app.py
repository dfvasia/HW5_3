import os

from flask import Flask, request
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def build_query(file: str, query: str):
    query_items = query.split("|")
    res = map(lambda x: x.strip(), file)
    for item in query_items:
        s_item = item.split(":")
        cmd = s_item[0]
        if cmd == "filter":  # с помощью функционального программирования (функций filter, map), итераторов/генераторов сконструировать запрос
            arg = s_item[1]
            res = filter(lambda t, txt=arg: txt in t, res)
        if cmd == "map":
            arg = int(s_item[1])
            res = map(lambda t, idx=arg: t.split(" ")[idx], res)
        if cmd == "unique":
            res = set(res)
        if cmd == "sort":
            arg = s_item[1]
            reverse = bool(arg == "desc")
            res = sorted(res, reverse=reverse)
        if cmd == "limit":
            arg = int(s_item[1])
            res = list(res)[:arg]
        return res


@app.route("/perform_query")
def perform_query():
    try:  # получить параметры query и file_name из request.args, при ошибке вернуть ошибку 400
        query = request.args["query"]
        file_name = request.args["file_name"]

    except KeyError:
        raise BadRequest

    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):  # проверить, что файла file_name существует в папке DATA_DIR, при ошибке вернуть ошибку 400
        return BadRequest(f"{file_name} was not found")

    with open(file_path) as f:
        res = build_query(f, query)
        data = '\n'.join(res)
        print(data)

    # вернуть пользователю сформированный результат
    return app.response_class(data, content_type="text/plain")
