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
            "message": "number is required"
        }), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT name, type FROM callers WHERE phone = %s LIMIT 1",
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

@app.route("/add", methods=["POST"])
def add():
    data = request.get_json(force=True)

    phone = str(data.get("phone", "")).strip()
    name = str(data.get("name", "")).strip()
    caller_type = str(data.get("type", "personal")).strip()

    if not phone or not name:
        return jsonify({
            "success": False,
            "message": "phone and name are required"
        }), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO callers (phone, name, type)
        VALUES (%s, %s, %s)
        ON CONFLICT (phone)
        DO UPDATE SET name = EXCLUDED.name, type = EXCLUDED.type
    """, (phone, name, caller_type))
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({
        "success": True,
        "message": "caller saved"
    })

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=10000)
else:
    init_db()
