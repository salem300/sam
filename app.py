import os
import psycopg2
from flask import Flask, jsonify, request

app = Flask(__name__)
app.json.ensure_ascii = False

DATABASE_URL = os.environ.get("DATABASE_URL")
ADMIN_API_KEY = os.environ.get("ADMIN_API_KEY")


def get_conn():
    return psycopg2.connect(DATABASE_URL)


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS callers (
            id SERIAL PRIMARY KEY,
            phone VARCHAR(30) UNIQUE NOT NULL,
            name VARCHAR(255) NOT NULL,
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


@app.route("/search")
def search():
    number = request.args.get("number", "").strip()

    if not number:
        return jsonify({
            "success": False,
            "error": "number parameter required"
        }), 400

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        "SELECT name, type FROM callers WHERE phone=%s LIMIT 1",
        (number,)
    )

    row = cur.fetchone()

    cur.close()
    conn.close()

    if row:
        return jsonify({
            "success": True,
            "number": number,
            "name": row[0],
            "type": row[1]
        })

    return jsonify({
        "success": False,
        "number": number,
        "name": None
    })


@app.route("/add_caller", methods=["POST"])
def add_caller():
    api_key = request.headers.get("x-api-key")

    if not ADMIN_API_KEY or api_key != ADMIN_API_KEY:
        return jsonify({
            "success": False,
            "error": "unauthorized"
        }), 401

    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "error": "invalid json"
        }), 400

    phone = str(data.get("phone", "")).strip()
    name = str(data.get("name", "")).strip()
    caller_type = str(data.get("type", "personal")).strip()

    if not phone or not name:
        return jsonify({
            "success": False,
            "error": "phone and name are required"
        }), 400

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO callers (phone, name, type)
        VALUES (%s, %s, %s)
        ON CONFLICT (phone)
        DO UPDATE SET name = EXCLUDED.name,
                      type = EXCLUDED.type
    """, (phone, name, caller_type))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "success": True,
        "message": "caller saved",
        "phone": phone,
        "name": name,
        "type": caller_type
    })


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
