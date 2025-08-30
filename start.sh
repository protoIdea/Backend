#!/bin/bash

# Budgetly Django Backend Startup Script

echo "🚀 Starting Budgetly Django Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp env.example .env
    echo "⚠️  Please edit .env file with your configuration before continuing"
    echo "Press Enter to continue..."
    read
fi

# Run Django checks
echo "🔍 Running Django system checks..."
python manage.py check

# Make and run migrations
echo "🗄️  Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if none exists
echo "👤 Checking for superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(is_superuser=True).exists():
    print('No superuser found. Please create one:')
    print('python manage.py createsuperuser')
else:
    print('Superuser already exists')
"

echo ""
echo "🎉 Setup completed!"
echo ""
echo "📋 To start the server:"
echo "   python manage.py runserver"
echo ""
echo "🌐 Access points:"
echo "   - Admin interface: http://localhost:8000/admin/"
echo "   - API endpoints: http://localhost:8000/api/"
echo "   - Frontend: http://localhost:3000/"
echo ""
echo "🔧 Additional commands:"
echo "   - Create superuser: python manage.py createsuperuser"
echo "   - Run tests: python manage.py test"
echo "   - Shell: python manage.py shell"
echo ""
echo "Press Enter to start the development server..."
read

# Start the development server
echo "🚀 Starting development server..."
python manage.py runserver

