from rest_framework import serializers
from airport.models import (
    Airport,
    Route,
    AirplaneType,
    Airplane,
    Crew,
    Flight,
    Order,
    Ticket,
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


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "created_at", "user"]
        read_only_fields = ["id", "created_at", "user"]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "row", "seat", "flight", "order"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        flight = attrs.get(
            "flight",
            self.instance.flight if self.instance else None,
        )
        order = attrs.get(
            "order",
            self.instance.order if self.instance else None,
        )
        row = attrs.get(
            "row",
            self.instance.row if self.instance else None,
        )
        seat = attrs.get(
            "seat",
            self.instance.seat if self.instance else None,
        )

        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication is required."
            )

        if order is not None and order.user_id != request.user.id:
            raise serializers.ValidationError({
                "order": "You cannot add tickets to another user's order.",
            })

        if flight is not None:
            airplane = flight.airplane

            if row is not None and row > airplane.rows:
                raise serializers.ValidationError({
                    "row": "Row number exceeds airplane capacity.",
                })

            if seat is not None and seat > airplane.seats_in_row:
                raise serializers.ValidationError({
                    "seat": "Seat number exceeds airplane capacity.",
                })

        if flight is not None and row is not None and seat is not None:
            existing_tickets = Ticket.objects.filter(
                flight=flight,
                row=row,
                seat=seat,
            )

            if self.instance:
                existing_tickets = existing_tickets.exclude(
                    pk=self.instance.pk
                )

            if existing_tickets.exists():
                raise serializers.ValidationError({
                    "seat": "This seat is already booked for this flight.",
                })

        return attrs

