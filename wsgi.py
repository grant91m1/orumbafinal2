# WSGI entrypoint for gunicorn / Render
# Export the Flask application object expected by WSGI servers.
from app import app as application

# Ensure the app is properly configured for production
if __name__ == '__main__':
    application.run()
