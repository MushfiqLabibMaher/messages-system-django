from django.db import connections
import logging

logger = logging.getLogger(__name__)

def setup_database():
    with connections['test'].cursor() as cursor:
        try:
            # Create users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                   id INT NOT NULL AUTO_INCREMENT,
                   username VARCHAR(255),
                   PRIMARY KEY (id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS admin (
                   id INT NOT NULL AUTO_INCREMENT,
                   admin_Name VARCHAR(255),
                   room_name VARCHAR(255) UNIQUE,
                   PRIMARY KEY (id)
                )
            """)

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_message (
                id INT AUTO_INCREMENT PRIMARY KEY,
                message TEXT NOT NULL,
                sender VARCHAR(255) NOT NULL,
                room_name_db VARCHAR(255) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (room_name_db) REFERENCES admin(room_name)
            );
        """)

        except Exception as e:
            logger.error(f"Error setting up database: {str(e)}")
            return False
    return True
