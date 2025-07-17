# ALX Travel App

A Django REST API application for travel booking management with asynchronous email processing using Celery and RabbitMQ.

## Features

- User management with role-based access (Guest, Host, Admin)
- Property listing management
- Booking system with status tracking
- Payment integration with Chapa payment gateway
- Background email notifications using Celery
- Review and rating system

## Technology Stack

- **Backend**: Django 5.2.3, Django REST Framework
- **Database**: SQLite (development), PostgreSQL-ready
- **Message Broker**: RabbitMQ
- **Task Queue**: Celery 5.5.3
- **Email**: SMTP (Zoho Mail)
- **Payment**: Chapa Payment Gateway
- **API Documentation**: drf-yasg (Swagger)

## Project Structure

```
alx_travel_app/
├── alx_travel_app/
│   ├── __init__.py
│   ├── settings.py          # Django configuration
│   ├── urls.py
│   ├── wsgi.py
│   └── celery.py           # Celery configuration
├── listings/
│   ├── models.py           # User, Listing, Booking, Payment, Review models
│   ├── views.py            # API viewsets
│   ├── serializers.py      # DRF serializers
│   ├── tasks.py            # Celery background tasks
│   ├── urls.py
│   └── admin.py
├── manage.py
├── db.sqlite3
└── .env                    # Environment variables
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
The application uses Celery for asynchronous email processing:

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
- RabbitMQ server
- Zoho Mail account (for email sending)
- Chapa account (for payments)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd alx_travel_app_0x03/alx_travel_app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # Linux/Mac
   # or env\Scripts\activate  # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   Create a `.env` file with:
   ```
   SECRET_KEY=your-django-secret-key
   DEBUG=True
   EMAIL_HOST_USER=your-email@zoho.com
   EMAIL_HOST_PASSWORD=your-zoho-app-password
   CHAPA_API_URL=https://api.chapa.co/v1/transaction/initialize
   CHAPA_VERIFY_URL=https://api.chapa.co/v1/transaction/verify/
   CHAPA_SECRET_KEY=CHASECK_TEST-your-test-key
   ```

5. **Setup database**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Start RabbitMQ**
   ```bash
   sudo rabbitmq-server -detached
   ```

7. **Start Celery worker**
   ```bash
   celery -A alx_travel_app worker --loglevel=info
   ```

8. **Start Django server**
   ```bash
   python manage.py runserver
   ```

## Configuration Details

### Celery Configuration
- **Broker**: RabbitMQ (amqp://guest:guest@localhost:5672//)
- **Result Backend**: Django database
- **Task Serializer**: JSON
- **Result Serializer**: JSON
- **Timezone**: UTC

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

## Production Considerations

1. **Database**: Switch to PostgreSQL
2. **Message Broker**: Use managed RabbitMQ service
3. **Email**: Configure production SMTP settings
4. **Security**: Use strong secret keys and HTTPS
5. **Monitoring**: Add Celery monitoring (Flower)
6. **Error Handling**: Implement task retry logic
7. **Scaling**: Consider multiple Celery workers

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
| DB_ENGINE | Database engine | No |
| DB_NAME | Database name | No |
| DB_USER | Database user | No |
| DB_PASSWORD | Database password | No |
| DB_HOST | Database host | No |
| DB_PORT | Database port | No |

## API Documentation

Access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and test thoroughly
4. Ensure all tests pass
5. Submit a pull request

## License

This project is part of the ALX Software Engineering Program.