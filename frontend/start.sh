#!/bin/bash

# Frontend Development Server Launcher
# This script starts the React development server for the chat frontend

echo "🚀 Starting Chat Frontend Development Server..."
echo "📍 Frontend Directory: $(pwd)"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ package.json not found. Please run this script from the frontend directory."
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies. Please check your npm installation."
        exit 1
    fi
fi

# Check if backend is running
echo "🔍 Checking if backend is running..."
if curl -s http://localhost:8000/api/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "⚠️  Warning: Backend doesn't seem to be running on http://localhost:8000"
    echo "   Make sure to start the backend before using the frontend"
    echo "   Run: cd ../backend && ./run_backend.sh"
fi

# Start the development server
echo ""
echo "🌟 Starting React development server..."
echo "💻 The app will open in your default browser"
echo "🔗 Frontend URL: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000/api/v1"
echo ""
echo "Press Ctrl+C to stop the development server"
echo ""

npm start