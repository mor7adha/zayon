import sqlite3

def init_db():
    conn = sqlite3.connect('academy.db')
    c = conn.cursor()

    # Create Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            national_id TEXT UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            gender TEXT NOT NULL,
            city TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create Programs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS programs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            duration TEXT NOT NULL,
            fee REAL NOT NULL,
            start_date TEXT NOT NULL
        )
    ''')

    # Create Enrollments table
    c.execute('''
        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            program_id INTEGER NOT NULL,
            enrollment_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (program_id) REFERENCES programs (id)
        )
    ''')

    # Check if programs already exist, if not insert default ones
    c.execute("SELECT COUNT(*) FROM programs")
    if c.fetchone()[0] == 0:
        default_programs = [
            ('Cyber Security', 'Technology', '30 Days', 1500.00, '2025-01-01'),
            ('Web Development', 'Programming', '45 Days', 2000.00, '2025-02-01'),
            ('Data Analysis', 'Data Science', '40 Days', 1800.00, '2026-06-10'),
            ('Artificial Intelligence', 'AI', '50 Days', 3000.00, '2026-07-01')
        ]
        c.executemany('''
            INSERT INTO programs (name, type, duration, fee, start_date)
            VALUES (?, ?, ?, ?, ?)
        ''', default_programs)
        print("Default training programs inserted.")

    conn.commit()
    conn.close()
    print("Database initialized successfully.")

if __name__ == '__main__':
    init_db()
