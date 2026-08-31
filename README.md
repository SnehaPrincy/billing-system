# Billing System

A Django-based billing system that handles customer billing, product management, taxation, cash denominations, payment validation, change calculation, purchase history, invoice generation, and asynchronous invoice email delivery using Django-Q2.

## Features

- Customer-based billing
- Multiple products per bill
- Dynamic billing item formset
- Product quantity management
- Automatic tax calculation
- Payment validation
- Insufficient payment validation
- Exact change validation using available cash denominations
- Automatic change calculation
- Cash denomination management
- Purchase invoice generation
- Previous purchase history
- Purchase detail view
- Asynchronous invoice email sending
- Django-Q2 background task processing
- HTML and plain-text invoice emails
- SMTP email configuration using environment variables
- PostgreSQL database support
- Environment-based configuration for sensitive settings

## Technologies

- Python
- Django
- Django-Q2
- PostgreSQL
- HTML
- CSS
- SMTP
- python-dotenv

## Project Structure

```text
billing-system/
│
├── billing/
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── services.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   ├── validators.py
│   └── views.py
│
├── config/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── templates/
│   └── billing/
│       ├── billing_form.html
│       ├── customer_purchases.html
│       ├── invoice.html
│       ├── invoice_email.html
│       ├── invoice_email.txt
│       └── purchase_detail.html
│
├── .env.example
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

## Core Billing Flow

```text
Customer
   │
   ▼
Billing Form
   │
   ├── Select Products
   ├── Enter Quantities
   ├── Enter Payment
   └── Enter Available Denominations
   │
   ▼
Validation
   │
   ├── Product Validation
   ├── Payment Validation
   └── Change Validation
   │
   ▼
Create Purchase
   │
   ├── Customer
   ├── Purchase Items
   ├── Tax
   ├── Payment
   └── Change
   │
   ▼
Invoice Page
   │
   ▼
Queue Invoice Email
   │
   ▼
Django-Q2 Worker
   │
   ▼
SMTP Email
   │
   ▼
Customer
```

## Billing Validation

The system validates payment before completing a purchase.

### Insufficient Payment

If the amount received is less than the amount payable, the purchase is rejected and an error message is displayed to the user.

Example:

```text
Amount payable: 15930.00
Amount received: 15000.00

Billing Error:
Insufficient payment.
```

### Exact Change Validation

The system checks whether the required change can be provided using the available denominations entered by the user.

If the required change cannot be formed from the available denominations, the purchase is rejected.

This prevents the system from completing a transaction when the requested change cannot actually be provided.

## Tax Calculation

Each product can have an associated tax percentage.

For example:

```text
Product Price: 50000.00
Quantity: 1
Tax: 18%

Tax Amount: 9000.00
Total: 59000.00
```

The invoice displays:

- Total before tax
- Total tax
- Total amount
- Rounded amount
- Paid amount
- Balance / Change

## Purchase History

The application provides a purchase history feature that allows previous purchases to be searched using the customer's email address.

The purchase history displays:

- Purchase ID
- Purchase date
- Total amount
- View Details action

Each purchase can then be opened to view its complete invoice details.

## Invoice Email

After a successful purchase, the invoice email is sent asynchronously using Django-Q2.

The email contains:

- Customer email
- Purchase ID
- Purchase date
- Purchased products
- Quantity
- Unit price
- Tax percentage
- Tax amount
- Product total
- Payment summary

The email supports both:

- HTML format
- Plain-text format

## Asynchronous Email Processing

Invoice emails are not sent directly during the user's billing request.

Instead, the application queues a background task:

```python
async_task(
    "billing.tasks.send_invoice_email",
    str(purchase.id),
)
```

Django-Q2 processes the task in the background.

This means the user does not have to wait for the email operation to complete before receiving the invoice page.

The flow is:

```text
Billing Request
      │
      ▼
Purchase Created
      │
      ▼
Invoice Email Task Queued
      │
      ▼
User Redirected to Invoice
      │
      │
      └──────────────► Django-Q2 Worker
                              │
                              ▼
                         Send Email
```

## Email Configuration

Email credentials are stored using environment variables rather than being hard-coded into the project.

Example `.env` configuration:

```env
SECRET_KEY=your_secret_key
DEBUG=True

DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432

EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

For Gmail SMTP, use a Gmail App Password rather than your normal Gmail account password.

The actual `.env` file should never be committed to GitHub.

## Environment Variables

The project uses environment variables for sensitive configuration such as:

- Django secret key
- Database credentials
- SMTP username
- SMTP password

A `.env.example` file is included as a template.

To configure the project:

```text
.env.example
     │
     ▼
Copy to .env
     │
     ▼
Add your local credentials
```

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/SnehaPrincy/billing-system.git
cd billing-system
```

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```text
billing-system/
├── .env
├── .env.example
├── manage.py
└── ...
```

Copy the values from `.env.example` and replace them with your local configuration.

### 5. Configure PostgreSQL

Create a PostgreSQL database and update the database values in `.env`.

Example:

```env
DB_NAME=billing_db
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 6. Run Migrations

```bash
python manage.py migrate
```

### 7. Create a Superuser

```bash
python manage.py createsuperuser
```

### 8. Run Django

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

## Running Django-Q2

Django-Q2 must run separately as a background worker.

Start the Q cluster with:

```bash
python manage.py qcluster
```

Keep the Q cluster running while testing asynchronous invoice emails.

## Testing Email Configuration

For development, Django can use the console email backend to display emails directly in the terminal.

For actual SMTP delivery, configure the SMTP backend and credentials in `.env`.

Example SMTP configuration:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_gmail_app_password
DEFAULT_FROM_EMAIL=your_email@gmail.com
```

After configuring SMTP, invoice emails can be processed by the Django-Q2 worker and delivered to the customer's email address.

## Running Tests

Run the Django test suite with:

```bash
python manage.py test
```

Verify the Django project configuration with:

```bash
python manage.py check
```

## Security

Sensitive credentials should never be committed to the repository.

The following should remain in `.env`:

```text
SECRET_KEY
DB_PASSWORD
EMAIL_HOST_PASSWORD
```

The `.env` file should be included in `.gitignore`.

Only `.env.example` should be committed to GitHub.

Example:

```text
.env
.venv/
venv/
__pycache__/
*.pyc
db.sqlite3
```

## Future Improvements

Possible future improvements include:

- User authentication
- Customer accounts
- PDF invoice generation
- Invoice download
- Invoice resend functionality
- Email delivery status tracking
- Django-Q2 task monitoring
- Failed email retry handling
- REST API
- Product inventory management
- Pagination for purchase history
- Improved frontend styling
- Production deployment
- Automated CI/CD testing

## Learning Objectives

This project demonstrates practical implementation of:

- Django models
- Django forms
- Formsets
- Model relationships
- Query optimization
- Service-layer architecture
- Business logic validation
- Database transactions
- Tax calculation
- Payment processing
- Cash denomination algorithms
- Purchase history
- Email templates
- SMTP configuration
- Environment variables
- Background task processing
- Django-Q2
- Git and GitHub workflow

## Author

**Sneha Princy**

GitHub: https://github.com/SnehaPrincy/billing-system

## License

This project is intended for learning and demonstration purposes.
