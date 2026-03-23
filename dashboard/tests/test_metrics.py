from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Requester, Pet, Booking


class DashboardMetricsTests(APITestCase):
    def setUp(self):
        """
        Create a controlled environment with specific numbers to test the math.
        """
        # 1. Create one requester
        self.requester = Requester.objects.create(name="Andrea", last_name="Gomez")

        # 2. Create 2 pets (1 cat, 1 dog) to test distribution
        self.cat = Pet.objects.create(
            name="Merlin", species="cat", requester=self.requester
        )
        self.dog = Pet.objects.create(
            name="Coco", species="dog", requester=self.requester
        )

        # 3. Create 2 bookings with specific prices
        # Total expected earnings: 100.50 + 49.50 = 150.00
        Booking.objects.create(
            pet=self.cat,
            start_date="2026-05-01T10:00:00Z",
            end_date="2026-05-05T10:00:00Z",
            price=100.50,
        )
        Booking.objects.create(
            pet=self.dog,
            start_date="2026-06-01T10:00:00Z",
            end_date="2026-06-05T10:00:00Z",
            price=49.50,
        )

        self.url = reverse("dashboard-metrics")

    def test_dashboard_metrics_accuracy(self):
        """
        GET: Verify the API returns the correct aggregated sums and counts.
        """
        response = self.client.get(self.url)

        # Check Status
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # 1. Check Total Pets (Should be 2)
        pet_data = response.data["pets"]
        self.assertEqual(pet_data["total_dogs"], 1)
        self.assertEqual(pet_data["total_cats"], 1)
        self.assertEqual(pet_data["total_pets"], 2)

        # 2. Check Total Earnings (Should be 150.00). The "Total Earnings" check ensures your Sum('price') isn't doubling up if a pet has multiple bookings.
        # We convert to float because Decimal becomes a string/float in JSON
        earnings_data = response.data["earnings"]
        total_expected = 100.50 + 49.50  # 150.00
        actual_total = earnings_data["past_earnings"] + earnings_data["future_earnings"]
        self.assertEqual(float(actual_total), total_expected)

        # For the bookings and reviews keys, since they contain serialized lists (which might change frequently), we often start by using assertIn. This confirms that the key exists in the dictionary.

        # 3. Testing the "bookings" nested object (The Serializers)
        # Check if the list exists (even if empty)
        self.assertIn("current_bookings", response.data["bookings"])
        self.assertIn("future_bookings", response.data["bookings"])

        # 4. Testing the "reviews" nested object
        self.assertIn("latest_reviews", response.data["reviews"])
