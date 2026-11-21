from rest_framework.routers import DefaultRouter

from airport.views import (
    AirportViewSet,
    RouteViewSet,
    AirplaneTypeViewSet,
    AirplaneViewSet,
    CrewViewSet,
    FlightViewSet,
)

router = DefaultRouter()

router.register('airports', AirportViewSet, basename='airport')
router.register('routes', RouteViewSet, basename='route')
router.register('airplane-types', AirplaneTypeViewSet, basename='airplane-type')
router.register('airplanes', AirplaneViewSet, basename='airplane')
router.register('crews', CrewViewSet, basename='crew')
router.register('flights', FlightViewSet, basename='flight')

urlpatterns = router.urls