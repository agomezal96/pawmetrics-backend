from django.urls import reverse
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Requester, Pet, Booking, Review

class SitterScoresTests(APITestCase):
    def setUp(self):
        self.now = timezone.now()
        self.six_months_ago = self.now - relativedelta(months=6)
        # Date out of the 6 months range
        self.seven_months_ago = self.now - relativedelta(months=7)

        # 1. Create owners
        self.owner_repeat = Requester.objects.create(name="Owner", last_name="Repeat")
        self.owner_unique = Requester.objects.create(name="Owner", last_name="Unique")
        self.owner_old = Requester.objects.create(name="Owner", last_name="Old")

        # 2. Pets
        self.pet_repeat = Pet.objects.create(name="Dog1", species="dog", requester=self.owner_repeat)
        self.pet_unique = Pet.objects.create(name="Dog2", species="dog", requester=self.owner_unique)
        self.pet_old = Pet.objects.create(name="Dog3", species="dog", requester=self.owner_old)

        # 3. Bookings for "Repeat Owner" (2 bookings in the last 6 months)
        Booking.objects.create(pet=self.pet_repeat, service='boarding', start_date=self.now - relativedelta(days=10), end_date=self.now - relativedelta(days=8), price=50)
        Booking.objects.create(pet=self.pet_repeat, service='boarding', start_date=self.now - relativedelta(days=5), end_date=self.now - relativedelta(days=3), price=50)

        # 4. Booking for "Unique Owner" (1 booking in the last 6 months)
        self.booking_unique = Booking.objects.create(pet=self.pet_unique, service='boarding', start_date=self.now - relativedelta(days=2), end_date=self.now, price=50)

        # 5. Old Booking (7 months ago - It should not count for the progress but for the global
        self.booking_old = Booking.objects.create(pet=self.pet_old, service='boarding', start_date=self.seven_months_ago, end_date=self.seven_months_ago + relativedelta(days=2), price=50)

        # 6. Reviews
        # Recent Review  (5 stars)
        Review.objects.create(booking=self.booking_unique, stars=5, description="Great!")
        # Old review (1 star - To see if it affects at the global average bot not to the 6 months average
        Review.objects.create(booking=self.booking_old, stars=1, description="Bad experience long ago")

        self.url = reverse("sitter-score")

    def test_sitter_scores_accuracy(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        progress = response.data["star_sitter_progress"]
        global_scores = response.data["global_score"]

        # --- Progress test (Last 6 months) ---
        
        # It should be 2 unique owners in the last 6 months (Repeat and Unique)
        # The "Old" doesn't count.
        self.assertEqual(progress["unique_owners"], 2)

        # It should be 1 repeated owner (owner_repeat has 2 bookings)
        self.assertEqual(progress["repeat_owners"], 1)

        # The last 6 months rating should be 5.0 
        self.assertEqual(progress["current_rating_6m"], 5.0)

        # --- Global Score Score (All time) ---
        
        # The total reviews should be 2 (the one 7 months ago and the current 
        self.assertEqual(global_scores["total_reviews"], 2)

        # The global average: (5 + 1) / 2 = 3.0
        self.assertEqual(global_scores["average_rating"], 3.0)