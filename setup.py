#!/usr/bin/env python3
"""
Setup script for Budgetly Django Backend
"""

import os
import sys
import subprocess
from pathlib import Path


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True,
                                check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False


def create_env_file():
    """Create .env file from example"""
    env_example = Path("env.example")
    env_file = Path(".env")

    if not env_file.exists() and env_example.exists():
        print("📝 Creating .env file from template...")
        with open(env_example, 'r') as f:
            content = f.read()

        # Generate a random secret key
        import secrets
        secret_key = 'django-insecure-' + secrets.token_urlsafe(50)
        content = content.replace(
            'your-secret-key-here-change-in-production', secret_key)

        with open(env_file, 'w') as f:
            f.write(content)
        print("✅ .env file created successfully")
        return True
    elif env_file.exists():
        print("ℹ️  .env file already exists")
        return True
    else:
        print("❌ env.example file not found")
        return False


def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'media', 'static', 'staticfiles']

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)

    print("✅ Directories created successfully")


def main():
    """Main setup function"""
    print("🚀 Setting up Budgetly Django Backend...")

    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Please run this script from the Backend directory")
        sys.exit(1)

    # Create .env file
    if not create_env_file():
        sys.exit(1)

    # Create directories
    create_directories()

    # Install dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)

    # Run Django checks
    if not run_command("python manage.py check", "Running Django system checks"):
        print("❌ Django system checks failed")
        sys.exit(1)

    # Make migrations
    if not run_command("python manage.py makemigrations", "Creating database migrations"):
        print("❌ Failed to create migrations")
        sys.exit(1)

    # Run migrations
    if not run_command("python manage.py migrate", "Running database migrations"):
        print("❌ Failed to run migrations")
        sys.exit(1)

    # Collect static files
    if not run_command("python manage.py collectstatic --noinput", "Collecting static files"):
        print("⚠️  Failed to collect static files (this is not critical)")

    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Create a superuser: python manage.py createsuperuser")
    print("2. Run the development server: python manage.py runserver")
    print("3. Access the admin interface at: http://localhost:8000/admin/")
    print("4. Access the API at: http://localhost:8000/api/")

    print("\n🔧 Additional setup (optional):")
    print("- Configure your database in .env file")
    print("- Set up Redis for Celery (if using background tasks)")
    print("- Configure email settings in .env file")


if __name__ == "__main__":
    main()

