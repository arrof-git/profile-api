
from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)

# Use the Render PostgreSQL URL (will be set as an environment variable)
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgres://app_user:password@host:port/profiles')

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
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
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('SELECT id, name, phone, last_modified FROM profiles')
    profiles = cursor.fetchall()
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
        cursor.execute('INSERT INTO profiles (id, name, phone, last_modified) VALUES (%s, %s, %s, %s)',
                       (id_, name, phone, last_modified))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Profile added'}), 201
    except psycopg2.IntegrityError:
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
    cursor.execute('UPDATE profiles SET name = %s, phone = %s, last_modified = %s WHERE id = %s',
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
    cursor.execute('DELETE FROM profiles WHERE id = %s', (id,))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Profile not found'}), 404
    conn.commit()
    conn.close()
    return jsonify({'message': 'Profile deleted'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
