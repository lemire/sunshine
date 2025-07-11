import sqlite3
import csv
import os

# Function to create the database and tables
def create_database(db_name):
    # Check if database file already exists
    if os.path.exists(db_name):
        raise FileExistsError(f"Error: Database {db_name} already exists.")

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create employers table
    cursor.execute('''
        CREATE TABLE employers (
            employer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_name TEXT NOT NULL,
            sector TEXT NOT NULL,
            UNIQUE(employer_name, sector)
        )
    ''')

    # Create individuals table
    cursor.execute('''
        CREATE TABLE individuals (
            individual_id INTEGER PRIMARY KEY AUTOINCREMENT,
            last_name TEXT NOT NULL,
            first_name TEXT NOT NULL,
            job_title TEXT NOT NULL,
            UNIQUE(last_name, first_name, job_title)
        )
    ''')

    # Create salaries table
    cursor.execute('''
        CREATE TABLE salaries (
            employer_id INTEGER,
            individual_id INTEGER,
            year INTEGER NOT NULL,
            salary REAL NOT NULL,
            benefits REAL NOT NULL,
            PRIMARY KEY (employer_id, individual_id, year),
            FOREIGN KEY (employer_id) REFERENCES employers (employer_id),
            FOREIGN KEY (individual_id) REFERENCES individuals (individual_id)
        )
    ''')

    conn.commit()
    return conn

# Function to load and normalize CSV data
def load_csv_to_db(csv_file, conn):
    cursor = conn.cursor()

    # Open and read the CSV file
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header row

        for row in reader:
            sector, last_name, first_name, salary, benefits, employer_name, job_title, year = row

            # Insert or get employer_id
            cursor.execute('''
                INSERT OR IGNORE INTO employers (employer_name, sector)
                VALUES (?, ?)
            ''', (employer_name, sector))
            cursor.execute('''
                SELECT employer_id FROM employers
                WHERE employer_name = ? AND sector = ?
            ''', (employer_name, sector))
            employer_id = cursor.fetchone()[0]

            # Insert or get individual_id
            cursor.execute('''
                INSERT OR IGNORE INTO individuals (last_name, first_name, job_title)
                VALUES (?, ?, ?)
            ''', (last_name, first_name, job_title))
            cursor.execute('''
                SELECT individual_id FROM individuals
                WHERE last_name = ? AND first_name = ? AND job_title = ?
            ''', (last_name, first_name, job_title))
            individual_id = cursor.fetchone()[0]

            # Replace commas in salary and benefits before converting to float
            salary = salary.replace(',', '')
            benefits = benefits.replace(',', '')

            # Insert into salaries table
            cursor.execute('''
                INSERT OR REPLACE INTO salaries (employer_id, individual_id, year, salary, benefits)
                VALUES (?, ?, ?, ?, ?)
            ''', (employer_id, individual_id, int(year), float(salary), float(benefits)))

    conn.commit()

# Main function
def main(csv_file, db_name):
    # Check if CSV file exists
    if not os.path.exists(csv_file):
        print(f"Error: {csv_file} not found.")
        return

    # Create database and load data
    try:
        conn = create_database(db_name)
        try:
            load_csv_to_db(csv_file, conn)
            print(f"Database {db_name} created and data loaded successfully from {csv_file}.")
        except Exception as e:
            print(f"An error occurred while loading data: {e}")
        finally:
            conn.close()
    except FileExistsError as e:
        print(e)
    except Exception as e:
        print(f"An error occurred while creating database: {e}")

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 3:
        print("Usage: python create_sunshine_db.py <csv_file> <db_name>")
    else:
        main(sys.argv[1], sys.argv[2])