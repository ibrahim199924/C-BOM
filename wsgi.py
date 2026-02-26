"""
WSGI entry point for production deployment.

Local dev:
    python main.py

Production (Render / Railway / Heroku):
    gunicorn wsgi:app

Production (Windows, no gunicorn):
    waitress-serve --host=0.0.0.0 --port=8000 wsgi:app

Environment variables:
    PORT  — Port to listen on (set automatically by cloud platforms)
"""

import os
from cbom.web_ui import create_app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
