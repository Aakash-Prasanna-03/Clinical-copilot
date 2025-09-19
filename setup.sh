#!/bin/bash

# Clinical Copilot Setup Script

echo "Setting up Clinical Copilot..."

# Setup Python backend
echo "Setting up Python backend..."
cd src

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate  # On Windows use: venv\Scripts\activate.bat

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Initialize vector database (if patient data exists)
if [ -f "patient_data.json" ]; then
    echo "Initializing vector database..."
    python embed.py
fi

echo "Python backend setup complete!"

# Setup frontend
echo "Setting up frontend..."
cd ../frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

echo "Frontend setup complete!"

echo "Setup complete!"
echo ""
echo "To start the application:"
echo "1. Start the Python backend: cd src && python app.py"
echo "2. Start the frontend: cd frontend && npm run dev"
echo ""
echo "Then visit http://localhost:3000"