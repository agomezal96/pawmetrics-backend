from django.contrib import admin
from .models import Requester, Pet, Booking, Review

# Register your models here.
admin.site.register(Requester)
admin.site.register(Pet)
admin.site.register(Booking)
admin.site.register(Review)