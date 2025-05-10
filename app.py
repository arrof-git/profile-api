
from flask import Flask, request, jsonify
import sqlite3
import os

app = Flask(__name__)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'profiles.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            last_modified TIMESTAMP NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_database()

@app.route('/profiles', methods=['GET'])
def get_profiles():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, phone, last_modified FROM profiles')
    profiles = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify(profiles)

@app.route('/profiles', methods=['POST'])
def add_profile():
    data = request.json
    id_ = data.get('id')
    name = data.get('name')
    phone = data.get('phone')
    last_modified = data.get('last_modified')
    if not all([id_, name, phone, last_modified]):
        return jsonify({'error': 'Missing fields'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO profiles (id, name, phone, last_modified) VALUES (?, ?, ?, ?)',
                      (id_, name, phone, last_modified))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Profile added'}), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Profile ID already exists'}), 400

@app.route('/profiles/<id>', methods=['PUT'])
def update_profile(id):
    data = request.json
    name = data.get('name')
    phone = data.get('phone')
    last_modified = data.get('last_modified')
    if not all([name, phone, last_modified]):
        return jsonify({'error': 'Missing fields'}), 400
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE profiles SET name = ?, phone = ?, last_modified = ? WHERE id = ?',
                  (name, phone, last_modified, id))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Profile not found'}), 404
    conn.commit()
    conn.close()
    return jsonify({'message': 'Profile updated'})

@app.route('/profiles/<id>', methods=['DELETE'])
def delete_profile(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM profiles WHERE id = ?', (id,))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Profile not found'}), 404
    conn.commit()
    conn.close()
    return jsonify({'message': 'Profile deleted'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
