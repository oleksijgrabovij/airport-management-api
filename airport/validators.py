from airport.models import Ticket


def is_seat_booked(flight, row, seat, exclude_ticket=None):
    if flight is None or row is None or seat is None:
        return False

    queryset = Ticket.objects.filter(
        flight=flight,
        row=row,
        seat=seat,
    )

    if exclude_ticket is not None and exclude_ticket.pk is not None:
        queryset = queryset.exclude(pk=exclude_ticket.pk)

    return queryset.exists()
