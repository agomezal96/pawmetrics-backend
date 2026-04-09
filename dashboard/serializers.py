from rest_framework import serializers
from .models import Requester, Pet, Booking, Review


class RequesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requester
        fields = ["id", "name", "last_name", "full_name", "image_url"]


class PetSerializer(serializers.ModelSerializer):
    requester_name = serializers.ReadOnlyField(source="requester.full_name")

    class Meta:
        model = Pet
        fields = ["id", "name", "species", "breed", "requester", "requester_name", "image_url"]


class BookingSerializer(serializers.ModelSerializer):
    pet_name = serializers.ReadOnlyField(source="pet.name")
    pet_species = serializers.ReadOnlyField(source="pet.species")
    pet_breed = serializers.ReadOnlyField(source="pet.breed")
    pet_image_url = serializers.ReadOnlyField(source="pet.image_url")

    # Booking -> Pet -> Requester -> full_name
    requester_name = serializers.ReadOnlyField(source="pet.requester.full_name")
    requester_image_url = serializers.ReadOnlyField(source="pet.requester.image_url")

    class Meta:
        model = Booking
        fields = [
            "id",
            "service",
            "start_date",
            "end_date",
            "price",
            "created_at",
            "pet",  # original ID from the pet
            "pet_name",
            "pet_species",
            "pet_breed",
            "pet_image_url",
            "requester_name",
            "requester_image_url",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    # Review -> Booking -> Pet -> Requester -> full_name
    requester_name = serializers.ReadOnlyField(source="booking.pet.requester.full_name")
    requester_image_url = serializers.ReadOnlyField(source="booking.pet.requester.image_url")

    class Meta:
        model = Review
        fields = [
            "id",
            "stars",
            "description",
            "created_at",
            "booking",
            "requester_name",
            "requester_image_url",
        ]
