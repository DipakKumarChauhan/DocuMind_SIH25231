#!/bin/bash
# Start FastAPI server for DocuMind

echo "🚀 Starting DocuMind FastAPI Server..."

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    else
        echo "⚠️  Warning: Virtual environment not found. Run ./install.sh first."
    fi
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "Please edit .env and add your API keys!"
    exit 1
fi

# Start server
echo ""
echo "Starting server at http://localhost:8000"
echo "Swagger docs: http://localhost:8000/docs"
echo "ReDoc: http://localhost:8000/redoc"
echo ""

python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload
