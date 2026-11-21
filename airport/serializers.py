from rest_framework import serializers
from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
)


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["id", "name", "closest_big_city"]


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["id", "name"]


class AirplaneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "name", "rows", "seats_in_row", "airplane_type"]


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "crew",
        ]

    def validate(self, attrs):
        departure_time = attrs.get(
            "departure_time",
            self.instance.departure_time if self.instance else None,
        )
        arrival_time = attrs.get(
            "arrival_time",
            self.instance.arrival_time if self.instance else None,
        )

        if (
            departure_time is not None
            and arrival_time is not None
            and arrival_time <= departure_time
        ):
            raise serializers.ValidationError({
                "arrival_time": "Arrival time must be later than departure time",
            })
        return attrs