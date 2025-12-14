import psycopg2
from psycopg2 import OperationalError

def check_db():
    conn_params = {
        'dbname': 'student_portal',
        'user': 'postgres',
        'password': '1234',
        'host': 'localhost',
        'port': '5432'
    }
    
    try:
        print("Attempting to connect to 'student_portal'...")
        conn = psycopg2.connect(**conn_params)
        conn.close()
        print("SUCCESS: Connected to 'student_portal' database.")
    except OperationalError as e:
        err_msg = str(e)
        if 'does not exist' in err_msg:
             print("PARTIAL SUCCESS: Server is running, but database 'student_portal' DOES NOT EXIST.")
             print("Attempting to connect to default 'postgres' database to create it...")
             try:
                 # Connect to default 'postgres' db to create the new one
                 conn_params['dbname'] = 'postgres'
                 conn = psycopg2.connect(**conn_params)
                 conn.autocommit = True
                 cur = conn.cursor()
                 cur.execute("CREATE DATABASE student_portal;")
                 cur.close()
                 conn.close()
                 print("SUCCESS: Database 'student_portal' created successfully.")
             except Exception as create_err:
                 print(f"FAILURE: Could not create database. Error: {create_err}")
        elif 'Connection refused' in err_msg:
            print("FAILURE: Connection refused. PostgreSQL server may NOT be running.")
        else:
            print(f"FAILURE: Connection error: {err_msg}")

if __name__ == "__main__":
    check_db()
