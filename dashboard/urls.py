from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RequesterViewSet, PetViewSet, BookingViewSet, ReviewViewSet, DashboardMetricsView, SitterScoresView

# Once we have the views, we have to tell Django in which address lives each of them. For ModelViewSet, Django uses Router

router = DefaultRouter()
# r means 'raw string'. It's a good practice in URLS.
router.register(r'requesters', RequesterViewSet)
router.register(r'pets', PetViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('metrics/', DashboardMetricsView.as_view(), name='dashboard-metrics'), #we use as_view() because is an APIView class
    path('metrics/sitter-score/', SitterScoresView.as_view(), name='sitter-score'), # <-- Nueva ruta
    path('', include(router.urls)) # include automatic routes
]