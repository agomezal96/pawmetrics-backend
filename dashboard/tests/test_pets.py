from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Requester, Pet

# We use rest_framework.test.APITestCase.
# Think of this as a "Super-Tool" that:
# Acts like a Browser/Postman (self.client).
# Knows how to look up your URLs (reverse).
# Checks if things are equal (assertEqual).


# We create a Class. Everything inside is one "Suite" of tests.
class PetAPITests(APITestCase):
    def setUp(self):
        """
        STEP 1: SETUP (The Fake World)
        This function runs AUTOMATICALLY before every test.
        """
        # Create a fake owner in the temporary test database
        self.requester = Requester.objects.create(name="Andrea", last_name="Gomez")

        # URL for Listing/Creating.  URL: /api/pets/
        # 'pet-detail' is the name the Router gave to our ViewSet automatically.

        self.list_url = reverse("pet-list")

    def test_get_pet_detail_success(self):
        """
        GET: Test retrieving a specific pet's details
        """
        # We create a pet SPECIFICALLY for this test
        pet = Pet.objects.create(name="Calima", species="cat", requester=self.requester)

        # We build the detail URL using the ID of the pet we just made
        # We pass the 'pk' (Primary Key) of the pet we just created.
        # Build the URL: /api/pets/1/

        detail_url = reverse("pet-detail", kwargs={"pk": pet.id})

        # THE ACTION: The 'client' (robot) performs a GET request
        response = self.client.get(detail_url)

        # CHECK 1: The Status Code
        # We expect 200 (OK). If it's 404 or 500, the test fails.
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # CHECK 2: The Data Accuracy
        # 'response.data' is the JSON object the API returned.
        # We check if the 'name' in the JSON is exactly 'Merlin'
        self.assertEqual(response.data["name"], "Calima")
        # We check if the 'species' is 'Cat'
        self.assertEqual(response.data["species"], "cat")

    def test_get_non_existent_pet_returns_404(self):
        """
        NEGATIVE TEST: What happens if we ask for a pet that doesn't exist?
        """
        # We build a URL for an ID that definitely doesn't exist (999)
        invalid_url = reverse("pet-detail", kwargs={"pk": 999})
        response = self.client.get(invalid_url)

        # We EXPECT a 404 Not Found. If the API returns 200, the test fails!
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
