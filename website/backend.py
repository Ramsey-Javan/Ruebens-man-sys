import os
import psycopg2
from psycopg2 import sql

def database_operation(data):
    """Perform database operations"""
    try:
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Example: Insert data into database
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