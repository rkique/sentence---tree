echo "🚀 Starting Vite dev server on port 3000..."
npm run dev & VITE_PID=$!

# Function to cleanup processes on exit
cleanup() {
    echo "🛑 Shutting down services..."
    kill $FLASK_PID 2>/dev/null
    kill $VITE_PID 2>/dev/null
    echo "✅ Services stopped"
    exit
}

trap cleanup INT TERM

wait
