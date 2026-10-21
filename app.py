import sqlite3, logging
from flask import Flask, render_template, request, jsonify
from jinja2 import Environment, FileSystemLoader

app = Flask(__name__)
env = Environment(loader=FileSystemLoader("templates"))

app.logger.setLevel(logging.INFO)

def get_connection():
    conn = sqlite3.connect('database.db')
    return conn

def init_db():
    with get_connection() as conn:
        conn.execute("""
        create table if not exists kv_store
        (key TEXT primary key, value TEXT not null)
        """)

def get_value(key):
    with get_connection() as conn:
        value = conn.execute("""
        select value from kv_store where key = ?
        """,
        (key,),).fetchone()

        if value is None:
            app.logger.warning("GET: NOT FOUND (key: %s)", key)
            return None

        return value[0]

def put_value(key, value):
    with get_connection() as conn:
        conn.execute("""
        insert into kv_store (key, value)
        values (?, ?)
        on conflict(key) do update set value=excluded.value
        """,
        (key, value,),)

def delete_value(key):
    with get_connection() as conn:
        conn.execute("""
        delete from kv_store where key = ?
        """,
        (key,),)
        app.logger.info("DELETE: Successfully deleted (key: %s)", key)

@app.route('/<string:key>', methods=["PUT", "POST"])
def put(key):
    value = request.get_json()["value"]

    if value is None:
        app.logger.warning("PUT: Request does not have value (key: %s)", key)

    put_value(key, value)
    app.logger.info("PUT: PUT key: %s, value: %s", key, value)
    return jsonify({"key":key, "value":value})

@app.route('/<string:key>', methods=["GET"])
def get(key):
    value = get_value(key)
    if value is None:
        return {"error": "GET: key NOT FOUND"}, 404
    return jsonify({"key":key, "value":value})

@app.route('/<string:key>', methods=["DELETE"])
def delete(key):
    delete_value(key)
    return key

if __name__ == "__main__":
    init_db()
    app.run()