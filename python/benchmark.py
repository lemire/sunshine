import sqlite3
import time
import os
import sys
import statistics

def run_query(conn, query, description, num_runs=10):
    """Execute a query multiple times and return the median execution time."""
    execution_times = []
    cursor = conn.cursor()
    
    for _ in range(num_runs):
        start_time = time.time()
        cursor.execute(query)
        cursor.fetchall()  # Ensure all results are fetched
        end_time = time.time()
        execution_times.append(end_time - start_time)
    
    median_time = statistics.median(execution_times)
    print(f"{description}: {median_time:.4f} seconds (median of {num_runs} runs)")
    return median_time

def benchmark_indexes(db_name):
    """Benchmark join operation with and without indexes."""
    # Check if database exists
    if not os.path.exists(db_name):
        print(f"Error: Database {db_name} not found.")
        return

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Define the join query
        query = '''
            SELECT i.last_name, i.first_name, e.employer_name, e.sector, s.salary, s.year
            FROM salaries s
            JOIN employers e ON s.employer_id = e.employer_id
            JOIN individuals i ON s.individual_id = i.individual_id
        '''

        # Step 1: Drop any existing indexes to ensure clean baseline
        cursor.execute('DROP INDEX IF EXISTS idx_salaries_employer_id')
        cursor.execute('DROP INDEX IF EXISTS idx_salaries_individual_id')
        conn.commit()

        # Step 2: Run query without indexes
        print("Running query without indexes...")
        time_without_indexes = run_query(conn, query, "Query without indexes", num_runs=10)

        # Step 3: Create indexes on join columns
        print("\nCreating indexes...")
        cursor.execute('CREATE INDEX idx_salaries_employer_id ON salaries(employer_id)')
        cursor.execute('CREATE INDEX idx_salaries_individual_id ON salaries(individual_id)')
        conn.commit()

        # Step 4: Run query with indexes
        print("Running query with indexes...")
        time_with_indexes = run_query(conn, query, "Query with indexes", num_runs=10)

        # Step 5: Calculate and display speedup
        if time_with_indexes > 0:
            speedup = time_without_indexes / time_with_indexes
            print(f"\nSpeedup with indexes: {speedup:.2f}x (based on median times)")
        else:
            print("\nSpeedup calculation not possible (median time with indexes is zero).")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python benchmark_indexes.py <db_name>")
        return

    db_name = sys.argv[1]
    print(f"Benchmarking database: {db_name}")
    benchmark_indexes(db_name)

if __name__ == '__main__':
    main()