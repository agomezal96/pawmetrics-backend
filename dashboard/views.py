# Calculation tools
from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone

from rest_framework import viewsets
from .models import Requester, Pet, Booking, Review
from .serializers import (
    RequesterSerializer,
    PetSerializer,
    BookingSerializer,
    ReviewSerializer,
)


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


class DashboardMetricsView(APIView):
    def get(self, request):
        now = timezone.now()
        # Count pets by species
        total_dogs = Pet.objects.filter(species="dog").count()
        total_cats = Pet.objects.filter(species="cat").count()
        # Total money
        # .aggregate returns a dicctionary, so we use ['price__sum']
        past_earnings = (
            Booking.objects.filter(end_date__lt=now).aggregate(Sum("price"))[
                "price__sum"
            ]
            or 0
        )
        future_earnings = (
            Booking.objects.filter(start_date__gt=now).aggregate(Sum("price"))[
                "price__sum"
            ]
            or 0
        )

        # Current bookings
        current_bookings_queryset = Booking.objects.filter(
            start_date__lte=now, end_date__gt=now
        ).order_by("end_date")

        # Future bookings
        # Filter the bookings by date and order it by most recent.
        future_bookings_queryset = Booking.objects.filter(start_date__gt=now).order_by(
            "start_date"
        )

        # SERIALIZATION: Translate these objects to JSON using the serializer. We use many=True because it is a list of bookings, not just one.
        current_serializer = BookingSerializer(current_bookings_queryset, many=True)
        future_serializer = BookingSerializer(future_bookings_queryset, many=True)

        # Last 3 reviews
        latest_reviews_queryset = Review.objects.all().order_by("-id")[:3]
        review_serializer = ReviewSerializer(latest_reviews_queryset, many=True)

        data = {
            "pets": {
                "total_dogs": total_dogs,
                "total_cats": total_cats,
                "total_pets": total_dogs + total_cats,
            },
            "earnings": {
                "past_earnings": float(past_earnings),
                "future_earnings": float(future_earnings),
            },
            "bookings": {
                "current_bookings": current_serializer.data,
                "future_bookings": future_serializer.data,
            },
            "reviews": {"latest_reviews": review_serializer.data},
        }
        return Response(data)
