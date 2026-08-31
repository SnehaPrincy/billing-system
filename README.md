# Billing System

A Django-based billing system that handles product billing, taxation, cash denominations, payment validation, change calculation, purchase history, and asynchronous invoice emails.

## Features

- Customer-based billing
- Multiple products per bill
- Dynamic billing item formset
- Product quantity management
- Tax calculation
- Payment validation
- Insufficient payment validation
- Exact change validation using available denominations
- Cash denomination management
- Automatic change calculation
- Purchase invoice generation
- Previous purchase history
- Purchase detail view
- Asynchronous invoice email sending
- Django-Q2 background task processing
- HTML and plain-text invoice emails
- SMTP email configuration using environment variables

## Technologies

- Python
- Django
- Django-Q2
- SQLite
- HTML/CSS
- SMTP

## Project Structure

```text
billing-system/
│
├── billing/
│   ├── migrations/
│   ├── forms.py
│   ├── models.py
│   ├── services.py
│   ├── tasks.py
│   ├── urls.py
│   └── views.py
│
├── config/
│   ├── settings.py
│   └── urls.py
│
├── templates/
├── manage.py
├── requirements.txt
├── .env.example
└── .gitignore