# apps.py
from django.apps import AppConfig
from .db_manager import setup_database  # Import the function from your db_manager

class ChatConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'

def ready(self):
        # Call setup_database when the app is ready
        try:
            setup_database()
        except Exception as e:
            # Log the exception if setup_database fails
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error setting up database: {e}")
