import sqlite3
import time
import os
import sys
import statistics

def run_query(conn, query, description, num_runs=15):
    """Execute a query multiple times and return the median execution time."""
    execution_times = []
    cursor = conn.cursor()
    
    print(f"\n{description} (individual run times):")
    for i in range(num_runs):
        start_time = time.time()
        cursor.execute(query)
        cursor.fetchone()  # Fetch the single result (average salary)
        end_time = time.time()
        run_time = end_time - start_time
        execution_times.append(run_time)
        print(f"  Run {i+1}: {run_time*1000*1000:.4f} us")
    
    median_time = statistics.median(execution_times)
    print(f"{description}: {median_time*1000*1000:.4f} us (median of {num_runs} runs)")
    return median_time

def benchmark_lastname_index(db_name):
    """Benchmark query for average salary of employees with last name Smith."""
    # Check if database exists
    if not os.path.exists(db_name):
        print(f"Error: Database {db_name} not found.")
        return

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Define the query to compute average salary for last name Smith
        query = '''
            SELECT AVG(s.salary)
            FROM salaries s
            JOIN individuals i ON s.individual_id = i.individual_id
            WHERE i.last_name = 'Smith'
        '''

        # Step 1: Drop any existing index to ensure clean baseline
        cursor.execute('DROP INDEX IF EXISTS idx_individuals_last_name')
        conn.commit()

        # Step 2: Run query without index
        print("Running query without index (15 runs)...")
        time_without_index = run_query(conn, query, "Query without index")

        # Step 3: Create index on last_name
        print("\nCreating index on individuals.last_name...")
        cursor.execute('CREATE INDEX idx_individuals_last_name ON individuals(last_name)')
        conn.commit()

        # Step 4: Run query with index
        print("\nRunning query with index (15 runs)...")
        time_with_index = run_query(conn, query, "Query with index")

        # Step 5: Calculate and display speedup
        if time_with_index > 0:
            speedup = time_without_index / time_with_index
            print(f"\nSpeedup with index: {speedup:.2f}x (based on median times)")
        else:
            print("\nSpeedup calculation not possible (median time with index is zero).")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

def main():
    if len(sys.argv) != 2:
        print("Usage: python benchmark_lastname_index.py <db_name>")
        return

    db_name = sys.argv[1]
    print(f"Benchmarking database: {db_name}")
    benchmark_lastname_index(db_name)

if __name__ == '__main__':
    main()