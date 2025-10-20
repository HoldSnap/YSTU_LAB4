from flask import Flask, request, jsonify
import psycopg2
import os
from urllib.parse import urlparse

app = Flask(__name__)

DATABASE_URL = os.environ.get('DATABASE_URL', 
    'postgresql://serverless_db_pbuu_user:HbrobWy1Z0ZxfFngM0VoQFAehgUcY6PX@dpg-d3r31su3jp1c7390b6c0-a/serverless_db_pbuu'
)

try:
    url = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT NOW()
            )
        """)
        conn.commit()
except Exception as e:
    print(f"Ошибка подключения к БД: {e}")
    conn = None


@app.route('/')
def home():
    return "Hello, Serverless + PostgreSQL!", 200, {'Content-Type': 'text/plain'}


@app.route('/save', methods=['POST'])
def save_message():
    if not conn:
        return jsonify({"error": "DB not connected"}), 500

    data = request.get_json()
    message = data.get('message', '') if data else ''

    if not message:
        return jsonify({"error": "Message is empty"}), 400

    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO messages (content) VALUES (%s)", (message,))
            conn.commit()
        return jsonify({"status": "saved", "message": message}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/messages', methods=['GET'])
def get_messages():
    if not conn:
        return jsonify({"error": "DB not connected"}), 500

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, content, created_at FROM messages ORDER BY id DESC LIMIT 10")
            rows = cur.fetchall()
        messages = [{"id": r[0], "text": r[1], "time": r[2].isoformat()} for r in rows]
        return jsonify(messages)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

