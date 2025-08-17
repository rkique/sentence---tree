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

# Start Flask backend
cd backend && . venv/bin/activate && python3 app.py &
FLASK_PID=$!

echo "Flask server started with PID: $FLASK_PID"
echo "Press Ctrl+C to stop the server"

# Wait for the Flask process to finish
wait $FLASK_PID