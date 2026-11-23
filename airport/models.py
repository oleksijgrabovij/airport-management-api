from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.conf import settings


class Airport(models.Model):
    name = models.CharField(max_length=100)
    closest_big_city = models.CharField(max_length=255)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name="departing_routes",
    )
    destination = models.ForeignKey(
        Airport,
        on_delete=models.PROTECT,
        related_name="arriving_routes",
    )
    distance = models.PositiveIntegerField()

    def __str__(self):
        return (
            f"{self.source.closest_big_city} -> "
            f"{self.destination.closest_big_city}"
        )

    class Meta:
        ordering = ["source_id", "destination_id", "id"]
        constraints = [
            models.CheckConstraint(
                condition=~models.Q(
                    source=models.F("destination")
                ),
                name="route_source_destination_different",
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.source_id is not None
            and self.destination_id is not None
            and self.source_id == self.destination_id
        ):
            raise ValidationError({
                "destination": (
                    "Source and destination airports must differ."
                )
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return self.name


class Airplane(models.Model):
    name = models.CharField(max_length=255)
    rows = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    seats_in_row = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    airplane_type = models.ForeignKey(
        AirplaneType,
        on_delete=models.PROTECT,
        related_name="airplanes",
    )

    class Meta:
        ordering = ["name", "id"]

    def __str__(self):
        return f"{self.name} ({self.airplane_type.name})"


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    class Meta:
        ordering = ["last_name", "first_name", "id"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Flight(models.Model):
    route = models.ForeignKey(
        Route,
        on_delete=models.PROTECT,
        related_name="flights",
    )
    airplane = models.ForeignKey(
        Airplane,
        on_delete=models.PROTECT,
        related_name="flights",
    )
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(
        Crew,
        related_name="flights",
    )

    def clean(self):
        super().clean()
        if (
            self.departure_time is not None
            and self.arrival_time is not None
            and self.arrival_time <= self.departure_time
        ):
            raise ValidationError({
                "arrival_time": (
                    "Arrival time must be later than departure time"
                ),
            })

    class Meta:
        ordering = ["departure_time", "id"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(
                    arrival_time__gt=models.F("departure_time")
                ),
                name="flight_arrival_after_departure",
            ),
        ]

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.route} | {self.departure_time}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders",
    )

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        if self.pk is None:
            return "Unsaved order"

        return f"Order #{self.pk}"


class Ticket(models.Model):
    row = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    seat = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
    )
    flight = models.ForeignKey(
        Flight,
        on_delete=models.PROTECT,
        related_name="tickets",
    )
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    class Meta:
        ordering = ["flight_id", "row", "seat", "id"]
        constraints = [
            models.UniqueConstraint(
                fields=["flight", "row", "seat"],
                name="unique_seat_per_flight",
            )
        ]

    def clean(self):
        super().clean()
        if self.flight_id is not None:
            airplane = self.flight.airplane

            if self.row is not None and self.row > airplane.rows:
                raise ValidationError({
                    "row": "Row number exceeds airplane capacity.",
                })

            if self.seat is not None and self.seat > airplane.seats_in_row:
                raise ValidationError({
                    "seat": "Seat number exceeds airplane capacity.",
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"Flight #{self.flight.pk} | Row {self.row} | Seat {self.seat}"
