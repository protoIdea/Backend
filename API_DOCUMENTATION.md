# Budgetly API Documentation

## Overview

The Budgetly API provides comprehensive endpoints for managing personal finances, budgets, expenses, and AI-powered budget advice. All endpoints return JSON responses and use JWT authentication.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

## Endpoints

### Authentication

#### POST /token/
Obtain JWT access and refresh tokens.

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### POST /token/refresh/
Refresh an expired access token.

**Request Body:**
```json
{
    "refresh": "your_refresh_token"
}
```

#### POST /token/verify/
Verify a token's validity.

**Request Body:**
```json
{
    "token": "your_access_token"
}
```

### User Management

#### POST /accounts/register/
Register a new user account.

**Request Body:**
```json
{
    "username": "newuser",
    "email": "user@example.com",
    "password": "secure_password",
    "password_confirm": "secure_password",
    "first_name": "John",
    "last_name": "Doe",
    "currency": "USD",
    "monthly_income": 5000.00
}
```

#### POST /accounts/login/
User login.

**Request Body:**
```json
{
    "username": "username",
    "password": "password"
}
```

#### GET /accounts/profile/
Get current user's profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

#### PUT /accounts/profile/
Update current user's profile.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "first_name": "Updated Name",
    "monthly_income": 6000.00
}
```

#### GET /accounts/dashboard/
Get user dashboard data including budget summary and expenses.

**Headers:**
```
Authorization: Bearer <access_token>
```

### Budgets

#### GET /budgets/
List all budgets for the authenticated user.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `status`: Filter by budget status (active, paused, completed, overdue)
- `budget_type`: Filter by budget type (monthly, weekly, yearly, custom)
- `is_active`: Filter by active status (true/false)

#### POST /budgets/
Create a new budget.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
    "name": "Monthly Budget",
    "description": "My monthly budget for essentials",
    "amount": 3000.00,
    "budget_type": "monthly",
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
}
```

#### GET /budgets/{id}/
Get budget details by ID.

#### PUT /budgets/{id}/
Update budget by ID.

#### DELETE /budgets/{id}/
Delete budget by ID.

### Expenses

#### GET /expenses/
List all expenses for the authenticated user.

**Query Parameters:**
- `start_date`: Filter expenses from this date (YYYY-MM-DD)
- `end_date`: Filter expenses until this date (YYYY-MM-DD)
- `category`: Filter by category ID
- `min_amount`: Minimum expense amount
- `max_amount`: Maximum expense amount
- `expense_type`: Filter by expense type (one_time, recurring, subscription)
- `payment_method`: Filter by payment method

#### POST /expenses/
Create a new expense.

**Request Body:**
```json
{
    "title": "Grocery Shopping",
    "description": "Weekly groceries",
    "amount": 150.00,
    "category": 1,
    "date": "2024-01-15",
    "expense_type": "one_time",
    "payment_method": "credit_card"
}
```

#### GET /expenses/{id}/
Get expense details by ID.

#### PUT /expenses/{id}/
Update expense by ID.

#### DELETE /expenses/{id}/
Delete expense by ID.

### Categories

#### GET /categories/
List all expense categories for the authenticated user.

**Query Parameters:**
- `category_type`: Filter by type (income, expense, transfer)
- `is_active`: Filter by active status
- `is_default`: Filter by default categories

#### POST /categories/
Create a new category.

**Request Body:**
```json
{
    "name": "Entertainment",
    "description": "Movies, games, and leisure activities",
    "color": "#be123c",
    "category_type": "expense",
    "budget_percentage": 15.00
}
```

#### GET /categories/{id}/
Get category details by ID.

#### PUT /categories/{id}/
Update category by ID.

#### DELETE /categories/{id}/
Delete category by ID.

#### GET /categories/stats/
Get category statistics and budget usage.

#### GET /categories/usage-report/
Get detailed category usage report.

### Budget Templates

#### GET /templates/
List available budget templates.

**Query Parameters:**
- `template_type`: Filter by template type (student, family, travel, etc.)
- `is_featured`: Filter featured templates
- `is_public`: Filter public templates

#### GET /templates/{id}/
Get template details by ID.

#### POST /templates/{id}/use/
Use a template to create a new budget.

**Request Body:**
```json
{
    "amount": 5000.00,
    "start_date": "2024-01-01"
}
```

### Chatbot

#### GET /chatbot/messages/
Get chat message history.

**Query Parameters:**
- `conversation_id`: Filter by conversation ID
- `limit`: Number of messages to return (default: 50)

#### POST /chatbot/messages/
Send a message to the AI chatbot.

**Request Body:**
```json
{
    "content": "How can I save money on groceries?",
    "conversation_id": "optional_conversation_id"
}
```

#### GET /chatbot/sessions/
Get chat session information.

## Error Handling

The API returns appropriate HTTP status codes and error messages:

### 400 Bad Request
```json
{
    "error": "Validation error",
    "details": {
        "field_name": ["Error message"]
    }
}
```

### 401 Unauthorized
```json
{
    "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
    "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
    "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
    "error": "Internal server error",
    "details": "Error description"
}
```

## Pagination

List endpoints support pagination with the following query parameters:
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Response Format:**
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/expenses/?page=3",
    "previous": "http://localhost:8000/api/expenses/?page=1",
    "results": [...]
}
```

## Filtering

Many endpoints support filtering using query parameters:

```
GET /api/expenses/?start_date=2024-01-01&category=1&min_amount=10.00
```

## Search

Search endpoints support text search:

```
GET /api/categories/?search=entertainment
```

## Ordering

List endpoints support ordering:

```
GET /api/expenses/?ordering=-date,-amount
```

## Rate Limiting

API requests are rate-limited to prevent abuse. Limits are:
- 1000 requests per hour for authenticated users
- 100 requests per hour for unauthenticated users

## Data Models

### User
- `id`: User ID
- `username`: Username
- `email`: Email address
- `first_name`: First name
- `last_name`: Last name
- `currency`: Preferred currency
- `monthly_income`: Monthly income
- `is_premium`: Premium user status
- `date_joined`: Account creation date

### Budget
- `id`: Budget ID
- `name`: Budget name
- `amount`: Total budget amount
- `budget_type`: Budget period type
- `start_date`: Budget start date
- `end_date`: Budget end date
- `status`: Budget status
- `is_active`: Active status

### Expense
- `id`: Expense ID
- `title`: Expense title
- `amount`: Expense amount
- `category`: Category ID
- `date`: Expense date
- `expense_type`: Type of expense
- `payment_method`: Payment method used
- `is_recurring`: Recurring expense flag

### Category
- `id`: Category ID
- `name`: Category name
- `description`: Category description
- `color`: Category color (hex)
- `category_type`: Category type
- `budget_percentage`: Budget allocation percentage

## Examples

### Complete Workflow

1. **Register and Login**
```bash
# Register
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123","password_confirm":"password123"}'

# Login
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

2. **Create Categories**
```bash
# Create food category
curl -X POST http://localhost:8000/api/categories/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Food","description":"Groceries and dining","color":"#d97706","budget_percentage":30.00}'
```

3. **Create Budget**
```bash
# Create monthly budget
curl -X POST http://localhost:8000/api/budgets/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Monthly Budget","amount":3000.00,"budget_type":"monthly","start_date":"2024-01-01"}'
```

4. **Add Expenses**
```bash
# Add grocery expense
curl -X POST http://localhost:8000/api/expenses/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"title":"Grocery Shopping","amount":150.00,"category":1,"date":"2024-01-15"}'
```

5. **Get Dashboard Data**
```bash
# Get user dashboard
curl -X GET http://localhost:8000/api/accounts/dashboard/ \
  -H "Authorization: Bearer <access_token>"
```

## Support

For API support and questions:
- Email: support@budgetly.com
- Documentation: This file
- Issues: GitHub repository issues
