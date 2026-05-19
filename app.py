from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'super_secret_academy_key'  # Needed for sessions

def get_db_connection():
    conn = sqlite3.connect('academy.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- HTML Routes ---
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/signup.html')
def signup():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/index.html')
def login_page():
    return redirect(url_for('index'))

@app.route('/dashboard.html')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/programs.html')
def programs():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('programs.html')

@app.route('/enrollments.html')
def enrollments():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('enrollments.html')

@app.route('/payment.html')
def payment():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('payment.html')

@app.route('/certificate.html')
def certificate():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('certificate.html')


# --- API Routes ---

@app.route('/api/signup', methods=['POST'])
def api_signup():
    data = request.json
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO users (first_name, last_name, national_id, phone, email, gender, city, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (data['firstName'], data['lastName'], data['nationalId'], data['phone'], data['email'], data['gender'], data['city'], data['password']))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'User registered successfully'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Email or National ID already registered'}), 400

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.json
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', (data['email'], data['password'])).fetchone()
    conn.close()
    
    if user:
        session['user_id'] = user['id']
        session['user_name'] = f"{user['first_name']} {user['last_name']}"
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST', 'GET'])
def api_logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/api/programs', methods=['GET'])
def api_programs():
    conn = get_db_connection()
    programs = conn.execute('SELECT * FROM programs').fetchall()
    conn.close()
    return jsonify([dict(p) for p in programs])

@app.route('/api/enrollments', methods=['GET'])
def api_enrollments():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    conn = get_db_connection()
    # Join enrollments with programs to get program details
    query = '''
        SELECT e.id as enrollment_id, e.program_id, e.status, e.enrollment_date,
               p.name, p.fee, p.duration, p.type, p.start_date
        FROM enrollments e
        JOIN programs p ON e.program_id = p.id
        WHERE e.user_id = ?
    '''
    enrollments = conn.execute(query, (session['user_id'],)).fetchall()
    conn.close()
    return jsonify([dict(e) for e in enrollments])

@app.route('/api/enroll', methods=['POST'])
def api_enroll():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    program_id = data.get('program_id')
    user_id = session['user_id']
    
    conn = get_db_connection()
    # Check if already enrolled
    existing = conn.execute('SELECT * FROM enrollments WHERE user_id = ? AND program_id = ?', (user_id, program_id)).fetchone()
    if existing:
        conn.close()
        return jsonify({'success': False, 'message': 'Already enrolled in this program'}), 400
        
    date_now = datetime.now().strftime('%Y-%m-%d')
    conn.execute('''
        INSERT INTO enrollments (user_id, program_id, enrollment_date, status)
        VALUES (?, ?, ?, 'Pending')
    ''', (user_id, program_id, date_now))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Successfully enrolled'})

@app.route('/api/pay', methods=['POST'])
def api_pay():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    data = request.json
    enrollment_id = data.get('enrollment_id')
    
    conn = get_db_connection()
    conn.execute('UPDATE enrollments SET status = "Completed" WHERE id = ? AND user_id = ?', (enrollment_id, session['user_id']))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Payment successful'})

if __name__ == '__main__':
    if not os.path.exists('academy.db'):
        from init_db import init_db
        init_db()
    app.run(debug=True)
