#!/bin/bash

# Dev script - Backend in separate folder structure
cleanup() {
    echo "Cleaning up..."
    if [ ! -z "$FLASK_PID" ]; then
        echo "Stopping Flask server (PID: $FLASK_PID)"
        kill $FLASK_PID 2>/dev/null
    fi
    
    FLASK_PORT=${FLASK_PORT:-5001}
    lsof -ti:$FLASK_PORT | xargs kill -9 2>/dev/null
    echo "Cleanup of port $FLASK_PORT complete"
}

# Set trap to run cleanup on script exit
trap cleanup EXIT INT TERM

# Activate virtual environment
source /opt/venv/bin/activate

pip list

# Change to backend directory
cd backend

# Set Flask environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Start Flask backend
python3 app.py &
FLASK_PID=$!
echo "Flask server started with PID: $FLASK_PID"

# Wait for Flask to finish
wait $FLASK_PID