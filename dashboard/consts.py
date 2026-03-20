from django.db import models

class PetSpecies(models.TextChoices):
    DOG = "dog"
    CAT = "cat"
