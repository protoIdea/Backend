@echo off
chcp 65001 >nul
echo 🚀 Starting Budgetly Django Backend...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install/update dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo 📝 Creating .env file...
    copy env.example .env
    echo ⚠️  Please edit .env file with your configuration before continuing
    pause
)

REM Run Django checks
echo 🔍 Running Django system checks...
python manage.py check

REM Make and run migrations
echo 🗄️  Setting up database...
python manage.py makemigrations
python manage.py migrate

REM Collect static files
echo 📁 Collecting static files...
python manage.py collectstatic --noinput

REM Create superuser if none exists
echo 👤 Checking for superuser...
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print('No superuser found. Please create one: python manage.py createsuperuser') if not User.objects.filter(is_superuser=True).exists() else print('Superuser already exists')"

echo.
echo 🎉 Setup completed!
echo.
echo 📋 To start the server:
echo    python manage.py runserver
echo.
echo 🌐 Access points:
echo    - Admin interface: http://localhost:8000/admin/
echo    - API endpoints: http://localhost:8000/api/
echo    - Frontend: http://localhost:3000/
echo.
echo 🔧 Additional commands:
echo    - Create superuser: python manage.py createsuperuser
echo    - Run tests: python manage.py test
echo    - Shell: python manage.py shell
echo.
pause

REM Start the development server
echo 🚀 Starting development server...
python manage.py runserver
