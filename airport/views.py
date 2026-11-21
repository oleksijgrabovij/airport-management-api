from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from airport.permissions import IsAdminOrReadOnly
from datetime import date
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

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
from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    AirplaneTypeSerializer,
    AirplaneSerializer,
    CrewSerializer,
    FlightSerializer,
    OrderSerializer,
    TicketSerializer,
)


class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAdminOrReadOnly]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [IsAdminOrReadOnly]


class AirplaneTypeViewSet(viewsets.ModelViewSet):
    queryset = AirplaneType.objects.all()
    serializer_class = AirplaneTypeSerializer
    permission_classes = [IsAdminOrReadOnly]


class AirplaneViewSet(viewsets.ModelViewSet):
    queryset = Airplane.objects.all()
    serializer_class = AirplaneSerializer
    permission_classes = [IsAdminOrReadOnly]


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer
    permission_classes = [IsAdminOrReadOnly]



class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.prefetch_related("crew")
    serializer_class = FlightSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = self.queryset

        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        departure_date = self.request.query_params.get("departure_date")

        for field, value in [
            ("source", source),
            ("destination", destination),
        ]:
            if value is not None:
                if (
                    not value.isascii()
                    or not value.isdecimal()
                    or len(value) > 19
                    or not 0 < int(value) <= 9223372036854775807
                ):
                    raise ValidationError({
                        field: "Enter a valid positive integer ID."
                    })

        if source is not None:
            queryset = queryset.filter(route__source_id=int(source))

        if destination is not None:
            queryset = queryset.filter(
                route__destination_id=int(destination)
            )

        if departure_date is not None:
            try:
                parsed_date = date.fromisoformat(departure_date)
            except ValueError:
                raise ValidationError({
                    "departure_date": "Date must be in YYYY-MM-DD format."
                })

            if parsed_date.isoformat() != departure_date:
                raise ValidationError({
                    "departure_date": "Date must be in YYYY-MM-DD format."
                })

            queryset = queryset.filter(
                departure_time__date=parsed_date
            )

        return queryset


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Ticket.objects.filter(
            order__user=self.request.user
        )

    def _save_ticket(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()

        except IntegrityError as exc:
            attrs = serializer.validated_data
            instance = serializer.instance

            flight = attrs.get(
                "flight",
                instance.flight if instance else None,
            )
            row = attrs.get(
                "row",
                instance.row if instance else None,
            )
            seat = attrs.get(
                "seat",
                instance.seat if instance else None,
            )

            if all(value is not None for value in (flight, row, seat)):
                existing_tickets = Ticket.objects.filter(
                    flight=flight,
                    row=row,
                    seat=seat,
                )

                if instance is not None and instance.pk is not None:
                    existing_tickets = existing_tickets.exclude(
                        pk=instance.pk
                    )

                if existing_tickets.exists():
                    raise ValidationError({
                        "seat": "This seat is already booked for this flight.",
                    }) from exc

            raise

    def perform_create(self, serializer):
        self._save_ticket(serializer)

    def perform_update(self, serializer):
        self._save_ticket(serializer)
