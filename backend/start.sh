#!/bin/bash
# Exit on error
set -o errexit

# Install dependencies provided in requirements.txt
pip install --upgrade pip
pip install -r requirements.txt

# Run the application using Gunicorn with Uvicorn workers
# This is much more robust than 'uvicorn' alone
exec gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
