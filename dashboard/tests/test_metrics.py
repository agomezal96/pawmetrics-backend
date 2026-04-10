from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Requester, Pet, Booking, Review
from dateutil.relativedelta import relativedelta


class DashboardMetricsTests(APITestCase):
    def setUp(self):
        """
        Create a controlled environment with specific numbers to test the math.
        """
        self.now = timezone.now()
        # 1. Create one requester
        self.requester_a = Requester.objects.create(name="Andrea", last_name="Gomez")
        self.requester_b = Requester.objects.create(name="Lara", last_name="Bautista")

        # 2. Create 2 pets (1 cat, 1 dog) to test distribution
        self.dog = Pet.objects.create(
            name="Coco", species="dog", requester=self.requester_a
        )
        self.cat = Pet.objects.create(
            name="Merlin", species="cat", requester=self.requester_b
        )

        # 3. Create past, current and future bookings
        self.past_booking_1 = Booking.objects.create(
            pet=self.cat,
            service='boarding',
            start_date=self.now - relativedelta(days=10),
            end_date=self.now - relativedelta(days=2),
            price=100.00,
        )
        
        self.past_booking_2 = Booking.objects.create(
            pet=self.cat,
            service='boarding',
            start_date=self.now - relativedelta(days=4),
            end_date=self.now - relativedelta(days=2),
            price=50.00,
        )
        # CURRENT: Started yesterday, ends tomorrow
        self.current_booking = Booking.objects.create(
            pet=self.dog,
            service="boarding",
            start_date=self.now - relativedelta(days=1),
            end_date=self.now + relativedelta(days=1),
            price=50.00,
        )
        # FUTURE: Starts in 5 days
        self.future_booking = Booking.objects.create(
            pet=self.dog,
            service="boarding",
            start_date=self.now + relativedelta(days=5),
            end_date=self.now + relativedelta(days=10),
            price=80.00,
        )

        # REVIEWS
        # Reviews with text (it should appear in latest_reviews)
        Review.objects.create(
            booking=self.past_booking_1,
            stars=5,
            description="Amazing sitter!",
            created_at=self.now - relativedelta(days=1),
        )
        
        # Reviews without text (it should not appear in latest_review)
        Review.objects.create(
            booking=self.past_booking_2,
            stars=4,
            description="",
            created_at=self.now,
        )

        self.metrics_url = reverse("dashboard-metrics")
        
    def test_dashboard_metrics_logic(self):
        "Verify that the metrics are correctly grouped by time and content."
        response = self.client.get(self.metrics_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Earnings: Past (100) vs Pending (50 current + 80 future = 130)
        earnings = response.data["earnings"]
        self.assertEqual(earnings["past_earnings"], 150.0)
        self.assertEqual(earnings["future_earnings"], 130.0)

        # Bookings: Check that there is one in each category
        bookings = response.data["bookings"]
        self.assertEqual(len(bookings["past_bookings"]), 2)
        self.assertEqual(len(bookings["current_bookings"]), 1)
        self.assertEqual(len(bookings["future_bookings"]), 1)

        # Reviews: Text filtering
        reviews = response.data["reviews"]
        self.assertEqual(len(reviews["latest_reviews"]), 1) # Only the one that has text
        self.assertEqual(reviews["total_reviews"], 2)       # But the total are 2        
        
    def test_period_filtering(self):
        """Verifies that the parameter ?period works)."""
        # If we filter by a period in which there's nothing it should return 0
        response = self.client.get(f"{self.metrics_url}?period=last_year")
        self.assertEqual(response.data["pets"]["total_pets"], 0)
    