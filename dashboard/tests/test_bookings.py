from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Requester, Pet, Booking


class BookingAPITests(APITestCase):
    def setUp(self):
        """
        Create the hierarchy: Owner -> Pet -> Booking
        """

        # 1. Create the Requester
        self.requester = Requester.objects.create(name="Andrea", last_name="Gomez")

        # 2. Create the Pet
        self.pet = Pet.objects.create(
            name="Calima", species="cat", requester=self.requester
        )

        # 3. Build the detail URL /api/bookings
        self.list_url = reverse("booking-list")

    def test_get_booking_detail_success(self):
        """
        GET: Test retrieving a specific booking's detail
        """
        # 1. Create the Booking
        booking = Booking.objects.create(
            pet=self.pet,
            start_date="2026-04-01",
            end_date="2026-04-05",
            price=120.00,
        )

        # 2. Create the URL: /api/bookings/1
        detail_url = reverse("booking-detail", kwargs={"pk": booking.id})

        # 3. The 'client' performs a GET request:
        response = self.client.get(detail_url)

        # 4. ASSERTS
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["start_date"], "2026-04-01T00:00:00Z")
        self.assertEqual(response.data["end_date"], "2026-04-05T00:00:00Z")

        # For prices, sometimes the API returns a string "120.00"
        # Wrapping it in float() is a safe bet for comparisons
        self.assertEqual(float(response.data["price"]), 120.00)

        # CHECKING THE PET NAME:
        # This will pass ONLY if your BookingSerializer includes "pet_name"
        self.assertEqual(response.data["pet_name"], "Calima")

    def test_booking_id_not_found(self):
        """
        Check 404 for a non-existent booking
        """
        invalid_url = reverse("booking-detail", kwargs={"pk": 9999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
