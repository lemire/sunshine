import sqlite3
import sys
import os

def dump_schema(db_name, output_file=None):
    """Dump the schema of an SQLite database."""
    if not os.path.exists(db_name):
        print(f"Error: Database {db_name} not found.")
        return

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        schema_output = []
        for table in tables:
            table_name = table[0]
            # Get the CREATE TABLE statement
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            schema = cursor.fetchone()[0]
            schema_output.append(schema + ';')

        # Include indexes, if any
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='index';")
        indexes = cursor.fetchall()
        for index in indexes:
            if index[0]:  # Ensure index SQL is not None
                schema_output.append(index[0] + ';')

        # Output the schema
        schema_text = '\n'.join(schema_output)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(schema_text)
            print(f"Schema dumped to {output_file}")
        else:
            print(schema_text)

        conn.close()
    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python dump_schema.py <db_name> [output_file]")
        return

    db_name = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) == 3 else None
    dump_schema(db_name, output_file)

if __name__ == '__main__':
    main()