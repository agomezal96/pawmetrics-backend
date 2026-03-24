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

    # GET

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

    # POST

    def test_create_booking_success(self):
        """
        POST: Test creating a booking with valid data
        """
        # 1. Define the payload. We use self.pet.id from the setUp to link the booking
        payload = {
            "pet": self.pet.id,
            "start_date": "2026-04-01T00:00:00Z",
            "end_date": "2026-04-05T00:00:00Z",
            "price": "150.00",
        }
        # 2. Action: Send the POST request
        response = self.client.post(self.list_url, payload, format="json")

        # 3. Assert: Check for 201 created.
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 4. Assert: Verify the database count increased
        # Since the DB was empty before this test (except for setUp) count should be 1
        self.assertEqual(Booking.objects.count(), 1)

        # 5. ASSERT: Verify the data in the DB matches the payload
        new_booking = Booking.objects.get()
        self.assertEqual(new_booking.pet.id, self.pet.id)
        self.assertEqual(float(new_booking.price), 150.00)

    def test_create_booking_required_fields(self):
        """
        PURIST TEST: Cycle through all required fields and ensure they fail if missing.
        """
        required_fields = ["pet", "start_date", "end_date", "price"]

        base_payload = {
            "pet": self.pet.id,
            "start_date": "2026-04-01T00:00:00Z",
            "end_date": "2026-04-05T00:00:00Z",
            "price": "150.00",
        }

        for field in required_fields:
            # 1. Copy the payload
            payload = base_payload.copy()
            # 2. Remove ONE required field
            payload.pop(field)

            # 3. Request and Check
            response = self.client.post(self.list_url, payload, format="json")

            # Message helps identify WHICH field failed in the terminal
            self.assertEqual(
                response.status_code,
                status.HTTP_400_BAD_REQUEST,
                msg=f"Field '{field}' should be required but the API accepted the request.",
            )

            # Check that the error message specifically mentions the field
            self.assertIn(field, response.data)
