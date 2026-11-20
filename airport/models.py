from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Airport(models.Model):
    name = models.CharField(max_length=100)
    closest_big_city = models.CharField(max_length=255)

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
        return f"{self.source.closest_big_city} -> {self.destination.closest_big_city}"


class AirplaneType(models.Model):
    name = models.CharField(max_length=255)

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

    def __str__(self):
        return f"{self.name} ({self.airplane_type.name})"


class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

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
                "arrival_time": "Arrival time must be later than departure time",
            })


    def __str__(self):
        return f"{self.route} | {self.departure_time}"
