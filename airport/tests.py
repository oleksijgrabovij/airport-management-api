
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

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


User = get_user_model()


class AirportAPITests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="testuser",
            password="TestPassword123!",
        )

        cls.other_user = User.objects.create_user(
            username="otheruser",
            password="TestPassword123!",
        )

        cls.admin_user = User.objects.create_user(
            username="adminuser",
            password="TestPassword123!",
            is_staff=True,
        )

        cls.source = Airport.objects.create(
            name="Boryspil Airport",
            closest_big_city="Kyiv",
        )

        cls.destination = Airport.objects.create(
            name="Lviv Airport",
            closest_big_city="Lviv",
        )

        cls.route = Route.objects.create(
            source=cls.source,
            destination=cls.destination,
            distance=500,
        )

        cls.airplane_type = AirplaneType.objects.create(
            name="Boeing 737",
        )

        cls.airplane = Airplane.objects.create(
            name="Test Airplane",
            rows=30,
            seats_in_row=6,
            airplane_type=cls.airplane_type,
        )

        cls.crew = Crew.objects.create(
            first_name="John",
            last_name="Smith",
        )

        cls.departure = timezone.now() + timedelta(days=5)

        cls.flight = Flight.objects.create(
            route=cls.route,
            airplane=cls.airplane,
            departure_time=cls.departure,
            arrival_time=cls.departure + timedelta(hours=3),
        )

        cls.flight.crew.add(cls.crew)

        cls.order = Order.objects.create(user=cls.user)
        cls.other_order = Order.objects.create(
            user=cls.other_user
        )

    # PUBLIC API

    def test_public_endpoints(self):
        endpoints = [
            "airports",
            "routes",
            "airplane-types",
            "airplanes",
            "crews",
            "flights",
        ]

        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.client.get(
                    f"/api/airport/{endpoint}/"
                )
                self.assertEqual(
                    response.status_code,
                    status.HTTP_200_OK,
                )

    # PERMISSIONS

    def test_regular_user_cannot_create_airport(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/airport/airports/",
            {
                "name": "Test Airport",
                "closest_big_city": "Kyiv",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_admin_can_create_airport(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            "/api/airport/airports/",
            {
                "name": "New Airport",
                "closest_big_city": "Odesa",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    # FLIGHT FILTERS

    def test_filter_flights(self):
        response = self.client.get(
            "/api/airport/flights/",
            {
                "source": self.source.pk,
                "destination": self.destination.pk,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)

    def test_filter_flights_by_date(self):
        departure_date = timezone.localtime(
            self.departure
        ).date().isoformat()

        response = self.client.get(
            "/api/airport/flights/",
            {"departure_date": departure_date},
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)

    def test_invalid_flight_filters(self):
        invalid_params = [
            {"source": "abc"},
            {"destination": "-5"},
            {"departure_date": "invalid-date"},
            {"departure_date": "2026-13-50"},
        ]

        for params in invalid_params:
            with self.subTest(params=params):
                response = self.client.get(
                    "/api/airport/flights/",
                    params,
                )

                self.assertEqual(
                    response.status_code,
                    status.HTTP_400_BAD_REQUEST,
                )

    def test_invalid_flight_time(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            "/api/airport/flights/",
            {
                "route": self.route.pk,
                "airplane": self.airplane.pk,
                "departure_time": (
                    self.departure + timedelta(hours=2)
                ).isoformat(),
                "arrival_time": (
                    self.departure + timedelta(hours=1)
                ).isoformat(),
                "crew": [self.crew.pk],
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    # ORDERS

    def test_create_order(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/airport/orders/",
            {},
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        order = Order.objects.get(pk=response.data["id"])
        self.assertEqual(order.user, self.user)

    def test_user_cannot_view_other_orders(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f"/api/airport/orders/{self.other_order.pk}/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

    # TICKETS

    def test_create_ticket(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/airport/tickets/",
            {
                "row": 5,
                "seat": 3,
                "flight": self.flight.pk,
                "order": self.order.pk,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

    def test_duplicate_ticket(self):
        Ticket.objects.create(
            row=5,
            seat=3,
            flight=self.flight,
            order=self.order,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/airport/tickets/",
            {
                "row": 5,
                "seat": 3,
                "flight": self.flight.pk,
                "order": self.order.pk,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_invalid_seat(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/airport/tickets/",
            {
                "row": 5,
                "seat": 100,
                "flight": self.flight.pk,
                "order": self.order.pk,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cannot_book_other_users_order(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/airport/tickets/",
            {
                "row": 5,
                "seat": 4,
                "flight": self.flight.pk,
                "order": self.other_order.pk,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_user_sees_only_own_tickets(self):
        Ticket.objects.create(
            row=1,
            seat=1,
            flight=self.flight,
            order=self.order,
        )

        Ticket.objects.create(
            row=1,
            seat=2,
            flight=self.flight,
            order=self.other_order,
        )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            "/api/airport/tickets/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(len(response.data), 1)

    # JWT AUTHENTICATION

    def test_jwt_authentication(self):
        response = self.client.post(
            "/api/token/",
            {
                "username": "testuser",
                "password": "TestPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        refresh_response = self.client.post(
            "/api/token/refresh/",
            {"refresh": response.data["refresh"]},
            format="json",
        )

        self.assertEqual(
            refresh_response.status_code,
            status.HTTP_200_OK,
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(
                f"Bearer {response.data['access']}"
            )
        )

        orders_response = self.client.get(
            "/api/airport/orders/"
        )

        self.assertEqual(
            orders_response.status_code,
            status.HTTP_200_OK,
        )
