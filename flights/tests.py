from django.test import TestCase, Client
from django.db.models import Max
from .models import Airport, Flight, Passenger

# Create your tests here.
class FlightsTestCase(TestCase):

    def setUp(self):

        # create airports
        a1 = Airport.objects.create(code="AAA", city="City A")
        a2 = Airport.objects.create(code="BBB", city="City B")

        # create flights
        Flight.objects.create(origin=a1, destination=a2, duration=100)
        Flight.objects.create(origin=a1, destination=a1, duration=500)
        Flight.objects.create(origin=a1, destination=a2, duration=-100)

    def test_departures_count(self):
        a = Airport.objects.get(code="AAA")
        self.assertEqual(a.departures.count(), 3)

    def test_arrivals_count(self):
        a = Airport.objects.get(code="AAA")
        self.assertEqual(a.arrivals.count(), 1)

    def test_valid_flight(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        f1 = Flight.objects.get(origin=a1, destination=a2, duration=100)
        self.assertTrue(f1.is_valid_flight())
    
    def test_invalid_flight_destinantion(self):
        a1 = Airport.objects.get(code="AAA")
        f1 = Flight.objects.get(origin=a1, destination=a1)
        self.assertFalse(f1.is_valid_flight())
    
    def test_invalid_flight_deration(self):
        a1 = Airport.objects.get(code="AAA")
        a2 = Airport.objects.get(code="BBB")
        f1 = Flight.objects.get(origin=a1, destination=a2, duration=-100)
        self.assertFalse(f1.is_valid_flight())

    def test_index(self):
        c = Client()
        response = c.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["flights"].count(), 3)

    def test_valid_flight_page(self):
        a1 = Airport.objects.get(code="AAA")
        f = Flight.objects.get(origin=a1, destination=a1)

        c = Client()
        response = c.get(f"/{f.id}")
        self.assertEqual(response.status_code, 200)

    def test_invalid_flight_page(self):
        max_id = Flight.objects.all().aggregate(Max("id"))["id__max"]

        c = Client()
        response = c.get(f"/{max_id + 1}")
        self.assertEqual(response.status_code, 404)

    def test_flight_page_passengers(self):
        f = Flight.objects.get(pk=1)
        p = Passenger.objects.create(first="Alice", second="Adams")
        f.passengers.add(p)

        c = Client()
        response = c.get(f"/{f.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['passengers'].count(), 1)

    def test_flight_page_nonpassengers(self):
        f = Flight.objects.get(pk=1)
        p = Passenger.objects.create(first="Alice", second="Adams")
       
        c = Client()
        response = c.get(f"/{f.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['non_passengers'].count(), 1)