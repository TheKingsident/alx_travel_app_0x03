# ALX Travel App


A Django REST API application for travel booking management with asynchronous email processing using Celery and Redis (production), deployed as an API-only backend on AWS EC2 with PostgreSQL, Gunicorn, and nginx reverse proxy. No frontend is included.

## Features

- User management with role-based access (Guest, Host, Admin)
- Property listing management
- Booking system with status tracking
- Payment integration with Chapa payment gateway
- Background email notifications using Celery
- Review and rating system

## Technology Stack

- **Backend**: Django 5.2.3, Django REST Framework
- **Database**: PostgreSQL (production), SQLite (development)
- **Message Broker**: Redis (production), RabbitMQ (development)
- **Task Queue**: Celery 5.5.3
- **Email**: SMTP (Zoho Mail)
- **Payment**: Chapa Payment Gateway
- **API Documentation**: drf-yasg (Swagger/OpenAPI)
- **Production Server**: Gunicorn (WSGI)
- **Reverse Proxy**: nginx (serves API on port 80)

## Project Structure

```
alx_travel_app/
├── alx_travel_app/
│   ├── __init__.py
│   ├── settings.py          # Django configuration (uses .env/.env.production)
│   ├── urls.py
│   ├── wsgi.py
│   ├── celery.py           # Celery configuration (switches broker by environment)
├── listings/
│   ├── models.py           # User, Listing, Booking, Payment, Review models
│   ├── views.py            # API viewsets
│   ├── serializers.py      # DRF serializers
│   ├── tasks.py            # Celery background tasks
│   ├── urls.py
│   └── admin.py
├── manage.py
├── db.sqlite3
├── .env                    # Development environment variables
├── .env.production         # Production environment variables
├── requirements.txt        # All dependencies (Django, DRF, Celery, Redis, Gunicorn, drf-yasg, etc.)
└── nginx.conf              # nginx reverse proxy config (see below)
```

## Models

### User
- Custom user model with roles (guest, host, admin)
- Email-based authentication
- Profile information (phone, role, timestamps)

### Listing
- Property listings with host relationship
- Title, description, location, pricing
- Active status management

### Booking
- Reservation system linking users and listings
- Date range, pricing, status tracking
- Status options: pending, confirmed, canceled

### Payment
- Payment tracking for bookings
- Chapa payment integration
- Transaction status management

### Review
- User reviews for listings
- Rating system (1-5 stars)
- Comment functionality

## API Endpoints

### Listings
- `GET /api/listings/` - List all active listings
- `POST /api/listings/` - Create new listing (hosts only)
- `GET /api/listings/{id}/` - Retrieve listing details
- `PUT/PATCH /api/listings/{id}/` - Update listing
- `DELETE /api/listings/{id}/` - Delete listing

### Bookings
- `GET /api/bookings/` - List user bookings
- `POST /api/bookings/` - Create new booking (triggers email)
- `GET /api/bookings/{id}/` - Retrieve booking details
- `PUT/PATCH /api/bookings/{id}/` - Update booking status

### Payments
- `POST /api/payments/initiate/` - Initialize payment with Chapa
- `POST /api/payments/verify/` - Verify payment status (triggers email)

## Background Tasks

### Email Notifications
The application uses Celery for asynchronous email processing. In production, Redis is used as the message broker (RabbitMQ is used for development only):

1. **Booking Confirmation Email**
   - Triggered when a new booking is created
   - Sent to customer with booking details
   - Task: `send_booking_confirmation_email`

2. **Payment Confirmation Email**
   - Triggered when payment is successfully verified
   - Sent to customer with payment confirmation
   - Task: `send_payment_confirmation_email`

## Setup Instructions

### Prerequisites
- Python 3.10+
- AWS EC2 instance (Amazon Linux 2023 recommended)
- PostgreSQL database (RDS or self-hosted)
- Redis server (for Celery in production)
- nginx (for reverse proxy)
- Gunicorn (WSGI server)
- Zoho Mail account (for email sending)
- Chapa account (for payments)

### Installation & Production Deployment

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd alx_travel_app_0x03/alx_travel_app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - For development: create `.env` in project root (see below)
   - For production: create `.env.production` with production values (see below)

5. **Setup PostgreSQL database**
   - Create a PostgreSQL database (e.g. on AWS RDS)
   - Update `.env.production` with DB credentials:
     ```
     DB_ENGINE=django.db.backends.postgresql
     DB_NAME=yourdbname
     DB_USER=yourdbuser
     DB_PASSWORD=yourdbpassword
     DB_HOST=yourdbhost
     DB_PORT=5432
     ```
   - Run migrations:
     ```bash
     python manage.py migrate
     python manage.py createsuperuser
     ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

7. **Install and start Redis (production)**
   ```bash
   sudo yum install redis6
   sudo systemctl enable redis6
   sudo systemctl start redis6
   ```

8. **Start Celery worker (production, using Redis)**
   ```bash
   source env/bin/activate
   celery -A alx_travel_app worker --loglevel=info
   ```

9. **Install Gunicorn and nginx**
   ```bash
   pip install gunicorn
   sudo yum install nginx
   ```

10. **Configure Gunicorn (WSGI server)**
    ```bash
    source env/bin/activate
    gunicorn alx_travel_app.wsgi:application --bind 127.0.0.1:8080 --env DJANGO_SETTINGS_MODULE=alx_travel_app.settings --env-file .env.production
    ```

11. **Configure nginx as reverse proxy**
    - Edit `/etc/nginx/nginx.conf` or add a site config:
      ```nginx
      server {
          listen 80;
          server_name api.kingsleyusa.dev travel.kingsleyusa.dev;
          location /static/ {
              alias /home/ec2-user/alx_travel_app_0x03/alx_travel_app/static/;
          }
          location / {
              proxy_pass http://127.0.0.1:8080;
              proxy_set_header Host $host;
              proxy_set_header X-Real-IP $remote_addr;
              proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
              proxy_set_header X-Forwarded-Proto $scheme;
          }
      }
      ```
    - Restart nginx:
      ```bash
      sudo systemctl restart nginx
      ```

12. **DNS Setup**
    - Point your subdomain (e.g. `api.kingsleyusa.dev`) to your EC2 public IP in your DNS provider (e.g. Namecheap)

13. **Test API**
    - Use `curl http://api.kingsleyusa.dev/` or your browser to verify the API is accessible

**Note:** For development, you can use SQLite, RabbitMQ, and run the Django dev server as before.

## Configuration Details

### Celery Configuration
- **Broker**: Redis (production: `redis://localhost:6379/0`), RabbitMQ (development: `amqp://guest:guest@localhost:5672//`)
- **Result Backend**: Django database
- **Task Serializer**: JSON
- **Result Serializer**: JSON
- **Timezone**: UTC

### Static Files
- Collected with `python manage.py collectstatic` and served by nginx in production

### Email Configuration
- **Backend**: SMTP
- **Host**: smtp.zoho.com
- **Port**: 587
- **TLS**: Enabled
- **Authentication**: Required

### Payment Integration
- **Provider**: Chapa
- **Currency**: ETB (Ethiopian Birr)
- **Environment**: Test/Live keys supported

## Development Workflow

1. **Create booking** via API
2. **Booking confirmation email** sent asynchronously
3. **Payment initialization** with Chapa
4. **Payment verification** and status update
5. **Payment confirmation email** sent asynchronously

## Testing

### Manual Testing
- Use Django Admin to create test data
- API testing via Postman or curl
- Email delivery testing with real email addresses

### Background Task Testing
```bash
# Test email tasks directly
python manage.py shell
>>> from listings.tasks import send_booking_confirmation_email
>>> result = send_booking_confirmation_email.delay('test@example.com', 'test-123', 'Test Property', '2025-08-01', '2025-08-07')
>>> result.get()
```

## Production Considerations & Troubleshooting

1. **API-Only Deployment**: No frontend is included; only the REST API is deployed.
2. **Database**: Use PostgreSQL in production (RDS recommended).
3. **Message Broker**: Use Redis in production (RabbitMQ is not available on Amazon Linux 2023).
4. **Static Files**: Must run `collectstatic` and serve via nginx for Swagger UI and docs to work.
5. **Gunicorn/nginx**: Gunicorn runs in virtualenv on port 8080; nginx proxies port 80 to Gunicorn.
6. **Custom Domain**: Set up DNS for your subdomain (e.g. `api.kingsleyusa.dev`) and add to `ALLOWED_HOSTS` (wildcard supported).
7. **Environment Variables**: Use `.env.production` for all production secrets and settings.
8. **Background Tasks**: Celery worker must be started with correct broker (Redis in production).
9. **Common Issues**:
   - 500 errors on booking: Check Celery/Redis are running and broker URL is correct
   - Static files/Swagger UI 404: Ensure `collectstatic` is run and nginx serves `/static/`
   - Gunicorn not found: Install in virtualenv and/or system Python if using sudo
   - Port 80 access: Use nginx as reverse proxy (Gunicorn should not run as root)
   - Browser cannot access API: Check DNS, security groups, and nginx config

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| SECRET_KEY | Django secret key | Yes |
| DEBUG | Debug mode (True/False) | Yes |
| EMAIL_HOST_USER | SMTP email address | Yes |
| EMAIL_HOST_PASSWORD | SMTP app password | Yes |
| CHAPA_API_URL | Chapa API endpoint | Yes |
| CHAPA_VERIFY_URL | Chapa verification endpoint | Yes |
| CHAPA_SECRET_KEY | Chapa secret key | Yes |
| DB_ENGINE | Database engine (use `django.db.backends.postgresql` for production) | Yes |
| DB_NAME | Database name | Yes |
| DB_USER | Database user | Yes |
| DB_PASSWORD | Database password | Yes |
| DB_HOST | Database host | Yes |
| DB_PORT | Database port | Yes |
| ALLOWED_HOSTS | Comma-separated list of allowed hosts (wildcard supported) | Yes |
| CELERY_BROKER_URL | Celery broker URL (use Redis in production) | Yes |

## API Documentation

Access the interactive API documentation at:
- Swagger UI: `http://<your-domain>/swagger/`
- ReDoc: `http://<your-domain>/redoc/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the ALX Software Engineering Program.