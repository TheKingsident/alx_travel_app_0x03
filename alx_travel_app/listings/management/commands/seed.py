import random
import uuid
from datetime import timedelta, date

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from listings.models import Listing, Booking, Review

from django.utils import timezone


class Command(BaseCommand):
    help = "Seed the database with sample data"

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        # Create users
        users = []
        for i in range(5):
            user, _ = User.objects.get_or_create(
                username=f'user{i}',
                defaults={'email': f'user{i}@example.com', 'password': 'password123'}
            )
            users.append(user)

        # Create listings
        listings = []
        for i in range(5):
            listing = Listing.objects.create(
                id=uuid.uuid4(),
                property=users[i % len(users)].properties.first(),  # assumes the user has properties
                title=f"Cozy Apartment {i}",
                description="A lovely place to stay.",
                price=round(random.uniform(30, 200), 2),
                is_active=True
            )
            listings.append(listing)

        # Create bookings
        for i in range(10):
            start_date = date.today() + timedelta(days=random.randint(1, 10))
            end_date = start_date + timedelta(days=random.randint(1, 5))
            listing = random.choice(listings)
            price_per_night = listing.price
            total_days = (end_date - start_date).days
            total_price = round(price_per_night * total_days, 2)

            Booking.objects.create(
                booking_id=uuid.uuid4(),
                listing=listing,
                user=random.choice(users),
                start_date=start_date,
                end_date=end_date,
                total_price=total_price,
                status=random.choice(['pending', 'confirmed', 'canceled']),
                created_at=timezone.now()
            )

        # Create reviews
        for i in range(10):
            Review.objects.create(
                review_id=uuid.uuid4(),
                listing=random.choice(listings),
                user=random.choice(users),
                rating=random.randint(1, 5),
                comment=f"This is review {i}. Great place!" if i % 2 == 0 else "Not bad.",
                created_at=timezone.now()
            )

        self.stdout.write(self.style.SUCCESS("Database seeded successfully."))
