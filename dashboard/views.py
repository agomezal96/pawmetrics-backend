# Calculation tools
from django.db.models import Sum, Count
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone

from rest_framework import viewsets
from .models import Requester, Pet, Booking, Review
from .consts import PetSpecies
from .serializers import (
    RequesterSerializer,
    PetSerializer,
    BookingSerializer,
    ReviewSerializer,
)

from .utils import get_period_range


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
        # 1. Recover the param that is sent by the frontend (period=3_months)
        period = request.query_params.get(
            "period", None
        )  # In Django Rest Framework, it is a dictionary that contains the URL parameters (what comes after the ?) The first parameter is the key you're looking for ('period'). The second is the default value if that key doesn't exist in the URL. We set it to None so that if the user enters /metrics/ without filters, the period variable will be None, and our logic will know not to filter anything (to retrieve everything).

        # 2. We obtain the date range:
        start, end = get_period_range(period)
        # 3. Create the base queryset. By default it brings everything, but if there is a 'start', we apply the time filter.
        bookings_qs = Booking.objects.all()  # In the database, the Booking is the common thread. Money comes from the Booking.com, pets are listed on the Booking.com, and reviews are based on a Booking.com. If you filter Booking by time, everything else is filtered automatically.
        if start and end:
            bookings_qs = bookings_qs.filter(start_date__lte=end, end_date__gte=start)

        # 4. Build the response by delegating to private methods. We pass them the filtered 'bookings_qs' to ensure consistency.

        data = {
            "pets": self._get_pet_stats(bookings_qs), # Pets from that bookings
            "earnings": self._get_earnings_stats(bookings_qs), # Money from that bookings
            "bookings": self._get_bookings_stats(bookings_qs), # Lists from that bookings
            "reviews": self._get_review_stats(bookings_qs), # Reviews from that bookings
        }

        return Response(data)

        # ---Support and private methods:

    def _get_pet_stats(self, qs):
        """Calculates pet statistics based on bookings for the period"""
        # We obtain the IDs of the unique pets that appear in those bookings

        # `values_list('pet', ...):` tells Django: "Don't retrieve the entire reservation object, just look at the `pet_id` field."
        # `flat=True`: By default, Django would give you a list of tuples: `[(5,), (2,), (5,)]`. Setting `flat` flattens it into a single list: `[5, 2, 5]`. This is much easier to work with.
        # `.distinct()`: This is the "non-duplicate" filter. In our example, the dog `5` appears twice. `.distinct()` clears the list, leaving you with: `[5, 2]`.

        pet_ids = qs.values_list("pet", flat=True).distinct()
        pets_in_period = Pet.objects.filter(id__in=pet_ids)

        # Count pets by species
        dogs = pets_in_period.filter(species=PetSpecies.DOG).count()
        cats = pets_in_period.filter(species=PetSpecies.CAT).count()

        return {
            "total_dogs": dogs,
            "total_cats": cats,
            "total_pets": dogs + cats,
        }

    def _get_earnings_stats(self, qs):
        """Calculates the past and future earnings inside the filtered period"""
        now = timezone.now()
        # We filter on the QS that already includes the time range
        past = qs.filter(end_date__lt=now).aggregate(Sum("price"))["price__sum"] or 0
        future = (
            qs.filter(start_date__gt=now).aggregate(Sum("price"))["price__sum"] or 0
        )

        return {
            "past_earnings": float(past),
            "future_earnings": float(future),
        }

    def _get_bookings_stats(self, qs):
        """Divide the bookings of the period based in past, current and future"""
        now = timezone.now()

        # Classify the bookings by time:

        past = qs.filter(end_date__lt=now).order_by("-end_date")
        current = qs.filter(start_date__lte=now, end_date__gt=now).order_by("end_date")
        future = qs.filter(start_date__gt=now).order_by("start_date")

        return {
            "past_bookings": BookingSerializer(past, many=True).data,
            "current_bookings": BookingSerializer(current, many=True).data,
            "future_bookings": BookingSerializer(future, many=True).data,
        }

    def _get_review_stats(self, qs):
        "Get the reviews linked to bookings for the selected period"
        # We just want the reviews of the bookings that are in our filtered queryset
        reviews = Review.objects.filter(booking__in=qs).order_by("-id")

        return {
            "latest_reviews": ReviewSerializer(reviews[:3], many=True).data,
            "total_reviews": reviews.count(),
        }
