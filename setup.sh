#!/bin/bash

echo "🚀 SAP O2C Graph Query System - Setup Script"
echo "=============================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GEMINI_API_KEY"
    echo ""
    read -p "Press Enter to open .env file for editing..."
    ${EDITOR:-nano} .env
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🔍 Checking prerequisites..."

# Check Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
else
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose is installed"
else
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo ""
echo "🏗️  Building and starting services..."
docker-compose up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

echo ""
echo "✅ Setup complete!"
echo ""
echo "📊 Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 View logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Stop services:"
echo "   docker-compose down"
echo ""
