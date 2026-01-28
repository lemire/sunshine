import sqlite3
import sys
import os

def explain_query_plan(conn, query, description):
    """Execute EXPLAIN QUERY PLAN for a given query and print the results."""
    cursor = conn.cursor()
    print(f"\n{description}")
    print("Query:")
    print(query.strip())
    print("\nEXPLAIN QUERY PLAN:")
    try:
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        rows = cursor.fetchall()
        for row in rows:
            print("  " + " | ".join(str(cell) for cell in row))
    except Exception as e:
        print(f"  Error: {e}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python explain_plan.py <db_name>")
        return

    db_name = sys.argv[1]

    # Check if database exists
    if not os.path.exists(db_name):
        print(f"Error: Database {db_name} not found.")
        return

    try:
        conn = sqlite3.connect(db_name)

        # First query: Join query for salaries with employer and individual details
        query1 = '''
            SELECT i.last_name, i.first_name, e.employer_name, e.sector, s.salary, s.year
            FROM salaries s
            JOIN employers e ON s.employer_id = e.employer_id
            JOIN individuals i ON s.individual_id = i.individual_id
        '''
        explain_query_plan(conn, query1, "Query 1: Join query for salaries with employer and individual details")

        # Second query: Average salary for last name 'Smith'
        query2 = '''
            SELECT AVG(s.salary)
            FROM salaries s
            JOIN individuals i ON s.individual_id = i.individual_id
            WHERE i.last_name = 'Smith'
        '''
        explain_query_plan(conn, query2, "Query 2: Average salary for individuals with last name 'Smith'")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    main()