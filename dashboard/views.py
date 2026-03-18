from rest_framework import viewsets
from .models import Requester, Pet, Booking, Review
from .serializers import RequesterSerializer, PetSerializer, BookingSerializer, ReviewSerializer

class RequesterViewSet(viewsets.ModelViewSet):
    queryset = Requester.objects.all()
    serializer_class = RequesterSerializer
    
class PetViewSet(viewsets.ModelViewSet):
    queryset = Pet.objects.all()
    serializer_class = PetSerializer
    
class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer