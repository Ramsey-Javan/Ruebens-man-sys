import os
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

# Load environment variables
load_dotenv()

def database_operation(data):
    """Perform database operations"""
    conn = None  # Ensure it's defined for use in finally block
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()

        # Insert data into transactions table
        query = sql.SQL("""
            INSERT INTO transactions (phone, amount, reference)
            VALUES (%s, %s, %s)
            RETURNING id, created_at
        """)

        cursor.execute(query, (
            data['phone'],
            data['amount'],
            data['account']
        ))

        result = cursor.fetchone()
        conn.commit()

        return {
            "id": result[0],
            "timestamp": result[1].isoformat()
        }

    except Exception as e:
        return {"error": str(e)}

    finally:
        if conn:
            conn.close()
