from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RequesterViewSet, PetViewSet, BookingViewSet, ReviewViewSet

# Once we have the views, we have to tell Django in which address lives each of them. For ModelViewSet, Django uses Router

router = DefaultRouter()
# r means 'raw string'. It's a good practice in URLS.
router.register(r'requesters', RequesterViewSet)
router.register(r'pets', PetViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls))
]