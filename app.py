import os
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS callers (
    ...
    type VARCHAR(50) DEFAULT 'personal'
);
    """)

    conn.commit()
    cur.close()
    conn.close()


@app.route("/")
def home():
    return jsonify({
        "status": "ok",
        "message": "Caller ID API Running"
    })


@app.route("/add_test")
def add_test():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO callers (phone, name, type)
        VALUES (%s, %s, %s)
        ON CONFLICT (phone) DO NOTHING
    """, (
        "966500000000",
        "محمد أحمد",
        "personal"
    ))

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "success": True,
        "message": "Test number added"
    })


@app.route("/search")
def search():
    number = request.args.get("number")

    if not number:
        return jsonify({
            "success": False,
            "error": "number parameter required"
        }), 400

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT name FROM callers WHERE phone=%s",
        (number,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return jsonify({
            "success": True,
            "number": number,
            "name": row[0]
        })

    return jsonify({
        "success": False,
        "number": number,
        "name": None
    })


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
