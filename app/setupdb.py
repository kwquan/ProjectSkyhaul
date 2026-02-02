import time
import psycopg2
from psycopg2.extras import RealDictCursor

while True:
    try:
        conn = psycopg2.connect(host='localhost', database='fastapi', user='postgres', 
                            password='12345', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        create_table_query = """
            CREATE TABLE IF NOT EXISTS telemetry (
                drone_id INT NOT NULL,
                mode VARCHAR NOT NULL,
                coordinate_x INT NOT NULL,
                coordinate_y INT NOT NULL,
                coordinate_z INT NOT NULL,
                fuel INT NOT NULL,
                state VARCHAR NOT NULL,
                timestamp TIMESTAMP
            )
        """
        
        # Execute the query
        cursor.execute(create_table_query)
        
        # Commit the changes to the database
        conn.commit()
        
        print("Table 'telemetry' created successfully")

        # Close the cursor
        cursor.close()
        break
    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)

