from django.contrib import admin
from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
)

admin.site.register(Airport)
admin.site.register(Route)
admin.site.register(AirplaneType)
admin.site.register(Airplane)
admin.site.register(Crew)
