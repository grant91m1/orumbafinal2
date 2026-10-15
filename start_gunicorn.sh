#!/bin/bash
# Start Gunicorn on the platform-provided port.
gunicorn -w 1 -b 0.0.0.0:${PORT:-8000} wsgi:application
