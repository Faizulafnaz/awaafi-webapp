# Awaafi Restaurant - Django Web Application

A modern restaurant ordering system built with Django, featuring user authentication, cart management, Stripe payments, and admin management.

## Features

- 🍽️ **Menu Management**: Categorized food items with variants
- 👤 **User Authentication**: Email-based login with Google OAuth
- 🛒 **Shopping Cart**: Add/remove items with quantity management
- 📍 **Address Management**: Multiple delivery addresses per user
- 💳 **Stripe Payments**: Secure checkout with Stripe integration
- 📧 **Email Notifications**: Order confirmations and contact forms
- 🔒 **Admin Panel**: Django Unfold admin interface with audit logging
- 📱 **Responsive Design**: Mobile-friendly interface

## Tech Stack

- **Backend**: Django 5.2.3
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: Django Allauth with Google OAuth
- **Payments**: Stripe
- **Admin**: Django Unfold
- **Static Files**: WhiteNoise
- **Deployment**: Render

## Local Development Setup

### Prerequisites

- Python 3.11+
- pip
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd awaafi
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

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your actual values
   ```

5. **Run migrations**
   ```bash
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

8. **Access the application**
   - Main site: http://localhost:8000
   - Admin panel: http://localhost:8000/admin

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
CONTACT_EMAIL=contact@yourdomain.com

# Stripe Settings
STRIPE_PK=pk_test_your_stripe_publishable_key
STRIPE_SK=sk_test_your_stripe_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
```

## Deployment on Render

### Prerequisites

- Render account
- GitHub repository with your code
- Stripe account for payments
- Email service (Gmail, SendGrid, etc.)

### Deployment Steps

1. **Connect your GitHub repository to Render**

2. **Create a new Web Service**
   - **Build Command**: `./build.sh`
   - **Start Command**: `gunicorn awaafi.wsgi:application`
   - **Environment**: Python 3.11+

3. **Set Environment Variables in Render Dashboard**
   ```env
   SECRET_KEY=your-production-secret-key
   DEBUG=False
   ALLOWED_HOSTS=your-app.onrender.com
   DATABASE_URL=postgresql://... (provided by Render)
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   CONTACT_EMAIL=contact@yourdomain.com
   STRIPE_PK=pk_live_your_stripe_publishable_key
   STRIPE_SK=sk_live_your_stripe_secret_key
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret
   ```

4. **Deploy**
   - Render will automatically build and deploy your application
   - The first deployment may take 5-10 minutes

### Post-Deployment Setup

1. **Create superuser**
   ```bash
   # Access Render shell or use Django admin
   python manage.py createsuperuser
   ```

2. **Set up Stripe webhook**
   - Go to Stripe Dashboard > Webhooks
   - Add endpoint: `https://your-app.onrender.com/stripe-webhook/`
   - Select events: `checkout.session.completed`

3. **Configure Google OAuth** (if using)
   - Update authorized redirect URIs in Google Console
   - Add: `https://your-app.onrender.com/accounts/google/login/callback/`

## Project Structure

```
awaafi/
├── awaafi/                 # Project settings
│   ├── settings.py        # Development settings
│   ├── settings_production.py  # Production settings
│   └── wsgi.py           # WSGI configuration
├── core/                  # Main app
│   ├── models.py         # Database models
│   ├── views.py          # Views and business logic
│   ├── admin.py          # Admin interface
│   └── urls.py           # URL routing
├── accounts/             # User management
│   ├── models.py         # Custom user model
│   └── views.py          # Authentication views
├── templates/            # HTML templates
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploaded files
├── requirements.txt      # Python dependencies
├── build.sh             # Render build script
└── manage.py            # Django management script
```

## Key Features Implementation

### Cart System
- Session-based cart for anonymous users
- Database cart for authenticated users
- Real-time quantity updates via AJAX

### Payment Integration
- Stripe Checkout for secure payments
- Webhook handling for order confirmation
- Automatic cart clearing after successful payment

### Admin Management
- Django Unfold for modern admin interface
- Audit logging with django-simple-history
- Role-based permissions (Manager, Staff, Kitchen)

## Security Considerations

- HTTPS enforced in production
- CSRF protection enabled
- XSS protection headers
- Secure session configuration
- Environment variables for sensitive data

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support, email contact@yourdomain.com or create an issue in the repository. 