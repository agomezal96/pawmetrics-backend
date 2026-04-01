from rest_framework import serializers
from .models import Requester, Pet, Booking, Review


class RequesterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requester
        fields = "__all__"


class PetSerializer(serializers.ModelSerializer):
    requester_name = serializers.ReadOnlyField(source="requester.full_name")

    class Meta:
        model = Pet
        fields = ["id", "name", "species", "breed", "requester", "requester_name"]


class BookingSerializer(serializers.ModelSerializer):
    pet_name = serializers.ReadOnlyField(source="pet.name")
    pet_species = serializers.ReadOnlyField(source="pet.species")
    # Booking -> Pet -> Requester -> full_name
    requester_name = serializers.ReadOnlyField(source="pet.requester.full_name")

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
            "requester_name",
        ]


class ReviewSerializer(serializers.ModelSerializer):
    # Review -> Booking -> Pet -> Requester -> full_name
    requester_name = serializers.ReadOnlyField(source="booking.pet.requester.full_name")

    class Meta:
        model = Review
        fields = ["id", "stars", "description", "booking", "requester_name"]
