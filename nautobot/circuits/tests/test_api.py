from django.urls import reverse

from nautobot.circuits.choices import CircuitTerminationSideChoices
from nautobot.circuits.models import Circuit, CircuitTermination, CircuitType, Provider, ProviderNetwork
from nautobot.core.testing import APITestCase, APIViewTestCases
from nautobot.dcim.models import Location
from nautobot.extras.models import Status


class AppTest(APITestCase):
    def test_root(self):
        url = reverse("circuits-api:api-root")
        response = self.client.get(f"{url}?format=api", **self.header)

        self.assertEqual(response.status_code, 200)


class ProviderTest(APIViewTestCases.APIViewTestCase):
    model = Provider
    brief_fields = ["circuit_count", "display", "id", "name", "url"]
    create_data = [
        {
            "name": "Provider 4",
        },
        {
            "name": "Provider 5",
        },
        {
            "name": "Provider 6",
        },
        {"name": "Provider 7"},
    ]
    bulk_update_data = {
        "asn": 1234,
    }


class ProviderNetworkTest(APIViewTestCases.APIViewTestCase):
    model = ProviderNetwork
    brief_fields = ["display", "id", "name", "slug", "url"]

    @classmethod
    def setUpTestData(cls):
        providers = Provider.objects.all()[:2]

        provider_networks = (
            ProviderNetwork(name="Provider Network 1", slug="provider-network-1", provider=providers[0]),
            ProviderNetwork(name="Provider Network 2", slug="provider-network-2", provider=providers[0]),
            ProviderNetwork(name="Provider Network 3", slug="provider-network-3", provider=providers[0]),
        )
        ProviderNetwork.objects.bulk_create(provider_networks)

        cls.create_data = [
            {
                "name": "Provider Network 4",
                "slug": "provider-network-4",
                "provider": providers[0].pk,
            },
            {
                "name": "Provider Network 5",
                "slug": "provider-network-5",
                "provider": providers[0].pk,
            },
            {
                "name": "Provider Network 6",
                "slug": "provider-network-6",
                "provider": providers[0].pk,
            },
        ]

        cls.bulk_update_data = {
            "provider": providers[1].pk,
            "description": "New description",
        }


class CircuitTypeTest(APIViewTestCases.APIViewTestCase):
    model = CircuitType
    brief_fields = ["circuit_count", "display", "id", "name", "url"]
    create_data = (
        {
            "name": "Circuit Type 4",
        },
        {
            "name": "Circuit Type 5",
        },
        {
            "name": "Circuit Type 6",
        },
        {"name": "Circuit Type 7"},
    )
    bulk_update_data = {
        "description": "New description",
    }

    @classmethod
    def setUpTestData(cls):
        CircuitType.objects.create(name="Circuit Type 1")
        CircuitType.objects.create(name="Circuit Type 2")
        CircuitType.objects.create(name="Circuit Type 3")


class CircuitTest(APIViewTestCases.APIViewTestCase):
    model = Circuit
    brief_fields = ["cid", "display", "id", "url"]

    @classmethod
    def setUpTestData(cls):
        providers = Provider.objects.all()[:2]

        circuit_types = CircuitType.objects.all()[:2]

        statuses = Status.objects.get_for_model(Circuit)

        Circuit.objects.create(
            cid="Circuit 1",
            provider=providers[0],
            circuit_type=circuit_types[0],
            status=statuses[0],
        )
        Circuit.objects.create(
            cid="Circuit 2",
            provider=providers[0],
            circuit_type=circuit_types[0],
            status=statuses[0],
        )
        Circuit.objects.create(
            cid="Circuit 3",
            provider=providers[0],
            circuit_type=circuit_types[0],
            status=statuses[0],
        )

        cls.create_data = [
            {
                "cid": "Circuit 4",
                "provider": providers[1].pk,
                "circuit_type": circuit_types[1].pk,
                "status": statuses[1].pk,
            },
            {
                "cid": "Circuit 5",
                "provider": providers[1].pk,
                "circuit_type": circuit_types[1].pk,
                "status": statuses[1].pk,
            },
            {
                "cid": "Circuit 6",
                "provider": providers[1].pk,
                "circuit_type": circuit_types[1].pk,
                "status": statuses[1].pk,
            },
        ]

        cls.bulk_update_data = {
            "status": statuses[2].pk,
        }


class CircuitTerminationTest(APIViewTestCases.APIViewTestCase):
    model = CircuitTermination
    brief_fields = ["cable", "circuit", "display", "id", "term_side", "url"]
    choices_fields = ["term_side"]

    @classmethod
    def setUpTestData(cls):
        SIDE_A = CircuitTerminationSideChoices.SIDE_A
        SIDE_Z = CircuitTerminationSideChoices.SIDE_Z

        locations = (
            Location.objects.first(),
            Location.objects.last(),
        )

        provider = Provider.objects.first()
        circuit_type = CircuitType.objects.first()

        circuits = (
            Circuit.objects.create(cid="Circuit 1", provider=provider, circuit_type=circuit_type),
            Circuit.objects.create(cid="Circuit 2", provider=provider, circuit_type=circuit_type),
            Circuit.objects.create(cid="Circuit 3", provider=provider, circuit_type=circuit_type),
        )

        CircuitTermination.objects.create(circuit=circuits[0], location=locations[0], term_side=SIDE_A)
        CircuitTermination.objects.create(circuit=circuits[0], location=locations[1], term_side=SIDE_Z)
        CircuitTermination.objects.create(circuit=circuits[1], location=locations[0], term_side=SIDE_A)
        CircuitTermination.objects.create(circuit=circuits[1], location=locations[1], term_side=SIDE_Z)

        cls.create_data = [
            {
                "circuit": circuits[2].pk,
                "term_side": SIDE_A,
                "location": locations[0].pk,
                "port_speed": 200000,
            },
            {
                "circuit": circuits[2].pk,
                "term_side": SIDE_Z,
                "location": locations[1].pk,
                "port_speed": 200000,
            },
        ]
        # Cannot use cls.create_data for test_update_object() here.
        # Because the first instance of CircuitTermination might have a provider_network
        # Setting a location on that instance will raise an validation error.
        cls.update_data = {
            "circuit": circuits[2].pk,
            "term_side": SIDE_A,
            "port_speed": 200000,
        }

        cls.bulk_update_data = {"port_speed": 123456}
