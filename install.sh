#!/bin/bash
# Quick installation and setup script for DocuMind

echo "🚀 DocuMind Installation Script"
echo "================================"

# Check Python version
echo ""
echo "Checking Python version..."
python3 --version || { echo "Error: Python 3.8+ required"; exit 1; }

# Create virtual environment
echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate || { echo "Error: Failed to activate venv"; exit 1; }

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt || { echo "Error: Installation failed"; exit 1; }

# Run setup script
echo ""
echo "Running setup script..."
python setup.py

# Create .env if needed
if [ ! -f ".env" ]; then
    echo ""
    echo "⚠️  .env file created. Please add your OpenAI API key:"
    echo "   OPENAI_API_KEY=your_api_key_here"
    echo ""
    read -p "Enter your OpenAI API key (or press Enter to skip): " api_key
    if [ ! -z "$api_key" ]; then
        sed -i "s/your_openai_api_key_here/$api_key/" .env
        echo "✓ API key saved to .env"
    fi
fi

echo ""
echo "================================"
echo "✅ Installation Complete!"
echo "================================"
echo ""
echo "Next steps:"
echo "1. Activate the environment: source venv/bin/activate"
echo "2. (If skipped) Edit .env and add your OpenAI API key"
echo "3. Run the app:"
echo "   - Streamlit UI: streamlit run ui/streamlit_app.py"
echo "   - CLI: python cli.py --help"
echo "   - Example: python example.py"
echo ""
echo "Happy hacking! 🎉"
