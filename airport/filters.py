from django import forms
from django_filters import rest_framework as filters

from airport.models import Flight


class AirportIdFilter(filters.NumberFilter):
    field_class = forms.IntegerField


class FlightFilter(filters.FilterSet):
    source = AirportIdFilter(
        field_name="route__source_id",
        min_value=1,
        max_value=9223372036854775807,
    )

    destination = AirportIdFilter(
        field_name="route__destination_id",
        min_value=1,
        max_value=9223372036854775807,
    )

    departure_date = filters.DateFilter(
        field_name="departure_time",
        lookup_expr="date",
    )

    class Meta:
        model = Flight
        fields = [
            "source",
            "destination",
            "departure_date",
        ]
