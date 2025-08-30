# Budgetly Django Backend

A comprehensive Django backend for the Budgetly budget management application, providing robust APIs for user management, budget tracking, expense management, and AI-powered chatbot functionality.

## Features

### 🔐 Authentication & User Management
- Custom User model with extended profile information
- JWT-based authentication with refresh tokens
- Password reset and change functionality
- User profile management with financial goals

### 💰 Budget Management
- Flexible budget periods (weekly, monthly, yearly, custom)
- Category-based budget allocation
- Budget templates for common scenarios
- Budget alerts and notifications
- Progress tracking and analytics

### 📊 Expense Tracking
- Comprehensive expense categorization
- Recurring expense support
- Receipt image uploads
- Payment method tracking
- Expense templates and reminders

### 🏷️ Category Management
- Custom expense categories with colors and icons
- Budget percentage allocation
- Category groups for organization
- Default category templates

### 🤖 AI Chatbot
- Intelligent budget advice and tips
- Context-aware conversations
- Knowledge base integration
- User interaction analytics

### 📱 API Features
- RESTful API design
- Comprehensive filtering and search
- Pagination and ordering
- CORS support for frontend integration

## Technology Stack

- **Framework**: Django 5.0.2
- **API**: Django REST Framework 3.15.1
- **Authentication**: JWT with Simple JWT
- **Database**: SQLite (default), PostgreSQL support
- **Task Queue**: Celery with Redis
- **File Storage**: Local storage with S3 support
- **Caching**: Redis
- **Documentation**: Django admin interface

## Installation

### Prerequisites
- Python 3.8+
- pip or pipenv
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Database setup**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

## Project Structure

```
Backend/
├── budgetly/                 # Main Django project
│   ├── __init__.py
│   ├── settings.py          # Project settings
│   ├── urls.py              # Main URL configuration
│   ├── wsgi.py              # WSGI configuration
│   └── asgi.py              # ASGI configuration
├── accounts/                 # User management app
│   ├── models.py            # User and Profile models
│   ├── serializers.py       # API serializers
│   ├── views.py             # API views
│   ├── urls.py              # URL patterns
│   └── admin.py             # Admin interface
├── budgets/                  # Budget management app
│   ├── models.py            # Budget and allocation models
│   ├── serializers.py       # Budget serializers
│   ├── views.py             # Budget views
│   ├── urls.py              # Budget URLs
│   └── admin.py             # Budget admin
├── expenses/                 # Expense tracking app
│   ├── models.py            # Expense models
│   ├── serializers.py       # Expense serializers
│   ├── views.py             # Expense views
│   ├── urls.py              # Expense URLs
│   └── admin.py             # Expense admin
├── categories/               # Category management app
│   ├── models.py            # Category models
│   ├── serializers.py       # Category serializers
│   ├── views.py             # Category views
│   ├── urls.py              # Category URLs
│   └── admin.py             # Category admin
├── templates/                # Budget templates app
│   ├── models.py            # Template models
│   ├── serializers.py       # Template serializers
│   ├── views.py             # Template views
│   ├── urls.py              # Template URLs
│   └── admin.py             # Template admin
├── chatbot/                  # AI chatbot app
│   ├── models.py            # Chat models
│   ├── serializers.py       # Chat serializers
│   ├── views.py             # Chat views
│   ├── urls.py              # Chat URLs
│   └── admin.py             # Chat admin
├── requirements.txt          # Python dependencies
├── manage.py                 # Django management script
├── env.example               # Environment variables example
└── README.md                 # This file
```

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `POST /api/token/verify/` - Verify JWT token

### User Management
- `POST /api/accounts/register/` - User registration
- `POST /api/accounts/login/` - User login
- `POST /api/accounts/logout/` - User logout
- `GET /api/accounts/profile/` - Get user profile
- `PUT /api/accounts/profile/` - Update user profile
- `GET /api/accounts/dashboard/` - User dashboard data

### Budgets
- `GET /api/budgets/` - List user budgets
- `POST /api/budgets/` - Create new budget
- `GET /api/budgets/{id}/` - Get budget details
- `PUT /api/budgets/{id}/` - Update budget
- `DELETE /api/budgets/{id}/` - Delete budget

### Expenses
- `GET /api/expenses/` - List user expenses
- `POST /api/expenses/` - Create new expense
- `GET /api/expenses/{id}/` - Get expense details
- `PUT /api/expenses/{id}/` - Update expense
- `DELETE /api/expenses/{id}/` - Delete expense

### Categories
- `GET /api/categories/` - List user categories
- `POST /api/categories/` - Create new category
- `GET /api/categories/{id}/` - Get category details
- `PUT /api/categories/{id}/` - Update category
- `DELETE /api/categories/{id}/` - Delete category

### Templates
- `GET /api/templates/` - List budget templates
- `POST /api/templates/` - Create new template
- `GET /api/templates/{id}/` - Get template details
- `POST /api/templates/{id}/use/` - Use template

### Chatbot
- `GET /api/chatbot/messages/` - Get chat history
- `POST /api/chatbot/messages/` - Send message
- `GET /api/chatbot/sessions/` - Get chat sessions

## Database Models

### Core Models
- **User**: Extended user model with financial preferences
- **UserProfile**: Additional user information and goals
- **Category**: Expense categories with budget allocation
- **Budget**: Budget periods with amounts and status
- **Expense**: Individual expense records
- **BudgetTemplate**: Reusable budget templates

### Advanced Features
- **ChatMessage**: AI chatbot conversation history
- **ChatSession**: Chat session management
- **BudgetAlert**: Budget threshold notifications
- **ExpenseReminder**: Recurring expense reminders

## Configuration

### Environment Variables
- `SECRET_KEY`: Django secret key
- `DEBUG`: Debug mode (True/False)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_ENGINE`: Database engine
- `DB_NAME`: Database name
- `EMAIL_*`: Email configuration
- `CELERY_*`: Celery configuration

### Database Configuration
The backend supports multiple database backends:
- **SQLite**: Default for development
- **PostgreSQL**: Recommended for production
- **MySQL**: Supported with additional configuration

### CORS Configuration
Configured for frontend integration:
- Allowed origins: localhost:3000, localhost:3001
- Credentials support enabled
- Customizable for production deployment

## Development

### Running Tests
```bash
python manage.py test
```

### Code Quality
```bash
python manage.py check
python manage.py validate
```

### Database Operations
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
```

### Admin Interface
Access the Django admin at `/admin/` after creating a superuser.

## Production Deployment

### Requirements
- Production-ready database (PostgreSQL recommended)
- Redis for caching and Celery
- Web server (Gunicorn + Nginx)
- Static file serving
- Environment variable management

### Deployment Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set secure `SECRET_KEY`
- [ ] Configure static file serving
- [ ] Set up SSL certificates
- [ ] Configure logging
- [ ] Set up monitoring
- [ ] Configure backups

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Email: support@budgetly.com
- Documentation: [API Documentation]
- Issues: [GitHub Issues]

## Acknowledgments

- Django community for the excellent framework
- Django REST Framework for robust API building
- All contributors to this project

