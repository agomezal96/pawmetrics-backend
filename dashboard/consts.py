from django.db import models

class PetSpecies(models.TextChoices):
    # Format: "db_value", "pretty_label"
    DOG = "dog", "Dog"
    CAT = "cat", "Cat"

class BookingService(models.TextChoices):
    BOARDING = "boarding", "Boarding"
    HOUSE_SITTING = "sitting", "House Sitting"
    DROP_IN = "drop_in", "Drop-in Visits"
    DAYCARE = "daycare", "Doggy Day Care"
    WALKING = "walking", "Dog Walking"