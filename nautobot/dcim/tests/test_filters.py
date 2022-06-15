import netaddr
from django.contrib.auth import get_user_model

from nautobot.dcim.choices import (
    CableLengthUnitChoices,
    CableTypeChoices,
    DeviceFaceChoices,
    InterfaceModeChoices,
    InterfaceTypeChoices,
    PortTypeChoices,
    PowerFeedPhaseChoices,
    PowerFeedSupplyChoices,
    PowerFeedTypeChoices,
    PowerOutletFeedLegChoices,
    RackDimensionUnitChoices,
    RackTypeChoices,
    RackWidthChoices,
    SubdeviceRoleChoices,
)
from nautobot.dcim.filters import (
    RegionFilterSet,
    SiteFilterSet,
    RackGroupFilterSet,
    RackRoleFilterSet,
    RackFilterSet,
    RackReservationFilterSet,
    ManufacturerFilterSet,
    DeviceTypeFilterSet,
    ConsolePortTemplateFilterSet,
    ConsoleServerPortTemplateFilterSet,
    PowerPortTemplateFilterSet,
    PowerOutletTemplateFilterSet,
    InterfaceTemplateFilterSet,
    FrontPortTemplateFilterSet,
    RearPortTemplateFilterSet,
    DeviceBayTemplateFilterSet,
    DeviceRoleFilterSet,
    PlatformFilterSet,
    DeviceFilterSet,
    ConsolePortFilterSet,
    ConsoleServerPortFilterSet,
    PowerPortFilterSet,
    PowerOutletFilterSet,
    InterfaceFilterSet,
    FrontPortFilterSet,
    RearPortFilterSet,
    DeviceBayFilterSet,
    InventoryItemFilterSet,
    VirtualChassisFilterSet,
    CableFilterSet,
    PowerPanelFilterSet,
    PowerFeedFilterSet,
)

from nautobot.dcim.models import (
    Cable,
    ConsolePort,
    ConsolePortTemplate,
    ConsoleServerPort,
    ConsoleServerPortTemplate,
    Device,
    DeviceBay,
    DeviceBayTemplate,
    DeviceRole,
    DeviceType,
    FrontPort,
    FrontPortTemplate,
    Interface,
    InterfaceTemplate,
    InventoryItem,
    Manufacturer,
    Platform,
    PowerFeed,
    PowerPanel,
    PowerPort,
    PowerPortTemplate,
    PowerOutlet,
    PowerOutletTemplate,
    Rack,
    RackGroup,
    RackReservation,
    RackRole,
    RearPort,
    RearPortTemplate,
    Region,
    Site,
    VirtualChassis,
)
from nautobot.circuits.models import Circuit, CircuitTermination, CircuitType, Provider
from nautobot.extras.models import SecretsGroup, Status
from nautobot.ipam.models import IPAddress, Prefix, VLAN, VLANGroup
from nautobot.tenancy.models import Tenant, TenantGroup
from nautobot.utilities.testing import FilterTestCases
from nautobot.virtualization.models import Cluster, ClusterType


# Use the proper swappable User model
User = get_user_model()


def common_test_data(cls):

    cls.tenant_groups = (
        TenantGroup.objects.create(name="Tenant group 1", slug="tenant-group-1"),
        TenantGroup.objects.create(name="Tenant group 2", slug="tenant-group-2"),
        TenantGroup.objects.create(name="Tenant group 3", slug="tenant-group-3"),
    )

    cls.tenants = (
        Tenant.objects.create(name="Tenant 1", slug="tenant-1", group=cls.tenant_groups[0]),
        Tenant.objects.create(name="Tenant 2", slug="tenant-2", group=cls.tenant_groups[1]),
        Tenant.objects.create(name="Tenant 3", slug="tenant-3", group=cls.tenant_groups[2]),
    )

    cls.regions = [
        Region.objects.create(name="Region 1", slug="region-1", description="A"),
        Region.objects.create(name="Region 2", slug="region-2", description="B"),
        Region.objects.create(name="Region 3", slug="region-3", description="C"),
    ]

    site_statuses = Status.objects.get_for_model(Site)
    cls.site_status_map = {s.slug: s for s in site_statuses.all()}

    cls.sites = [
        Site.objects.create(
            name="Site 1",
            slug="site-1",
            description="Site 1 description",
            region=cls.regions[0],
            tenant=cls.tenants[0],
            status=cls.site_status_map["active"],
            facility="Facility 1",
            asn=65001,
            latitude=10,
            longitude=10,
            contact_name="Contact 1",
            contact_phone="123-555-0001",
            contact_email="contact1@example.com",
            physical_address="1 road st, albany, ny",
            shipping_address="PO Box 1, albany, ny",
            comments="comment1",
            time_zone="America/Chicago",
        ),
        Site.objects.create(
            name="Site 2",
            slug="site-2",
            description="Site 2 description",
            region=cls.regions[1],
            tenant=cls.tenants[1],
            status=cls.site_status_map["planned"],
            facility="Facility 2",
            asn=65002,
            latitude=20,
            longitude=20,
            contact_name="Contact 2",
            contact_phone="123-555-0002",
            contact_email="contact2@example.com",
            physical_address="2 road st, albany, ny",
            shipping_address="PO Box 2, albany, ny",
            comments="comment2",
            time_zone="America/Los_Angeles",
        ),
        Site.objects.create(
            name="Site 3",
            slug="site-3",
            region=cls.regions[2],
            tenant=cls.tenants[2],
            status=cls.site_status_map["retired"],
            facility="Facility 3",
            asn=65003,
            latitude=30,
            longitude=30,
            contact_name="Contact 3",
            contact_phone="123-555-0003",
            contact_email="contact3@example.com",
            comments="comment3",
            time_zone="America/Detroit",
        ),
    ]

    provider = Provider.objects.create(name="Provider 1", slug="provider-1", asn=65001, account="1234")
    circuit_type = CircuitType.objects.create(name="Test Circuit Type 1", slug="test-circuit-type-1")
    circuit = Circuit.objects.create(provider=provider, type=circuit_type, cid="Test Circuit 1")
    cls.circuit_terminations = (
        CircuitTermination.objects.create(circuit=circuit, site=cls.sites[0], term_side="A"),
        CircuitTermination.objects.create(circuit=circuit, site=cls.sites[1], term_side="Z"),
    )

    manufacturers = (
        Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1"),
        Manufacturer.objects.create(name="Manufacturer 2", slug="manufacturer-2"),
        Manufacturer.objects.create(name="Manufacturer 3", slug="manufacturer-3"),
    )

    device_types = (
        DeviceType.objects.create(
            manufacturer=manufacturers[0],
            comments="Device type 1",
            model="Model 1",
            slug="model-1",
            part_number="Part Number 1",
            u_height=1,
            is_full_depth=True,
        ),
        DeviceType.objects.create(
            manufacturer=manufacturers[1],
            comments="Device type 2",
            model="Model 2",
            slug="model-2",
            part_number="Part Number 2",
            u_height=2,
            is_full_depth=True,
            subdevice_role=SubdeviceRoleChoices.ROLE_PARENT,
        ),
        DeviceType.objects.create(
            manufacturer=manufacturers[2],
            comments="Device type 3",
            model="Model 3",
            slug="model-3",
            part_number="Part Number 3",
            u_height=3,
            is_full_depth=False,
            subdevice_role=SubdeviceRoleChoices.ROLE_CHILD,
        ),
    )

    device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")
    device_statuses = Status.objects.get_for_model(Device)
    device_status_map = {ds.slug: ds for ds in device_statuses.all()}

    cls.rack_groups = (
        RackGroup.objects.create(name="Rack Group 1", slug="rack-group-1", site=cls.sites[0]),
        RackGroup.objects.create(name="Rack Group 2", slug="rack-group-2", site=cls.sites[1]),
        RackGroup.objects.create(name="Rack Group 3", slug="rack-group-3", site=cls.sites[2]),
    )

    cls.powerpanels = (
        PowerPanel.objects.create(name="Power Panel 1", site=cls.sites[0], rack_group=cls.rack_groups[0]),
        PowerPanel.objects.create(name="Power Panel 2", site=cls.sites[1], rack_group=cls.rack_groups[1]),
        PowerPanel.objects.create(name="Power Panel 3", site=cls.sites[2], rack_group=cls.rack_groups[2]),
    )

    cls.rackroles = (
        RackRole.objects.create(name="Rack Role 1", slug="rack-role-1", color="ff0000"),
        RackRole.objects.create(name="Rack Role 2", slug="rack-role-2", color="00ff00"),
        RackRole.objects.create(name="Rack Role 3", slug="rack-role-3", color="0000ff"),
    )

    rack_statuses = Status.objects.get_for_model(Rack)
    cls.rack_status_map = {s.slug: s for s in rack_statuses.all()}

    cls.racks = (
        Rack.objects.create(
            name="Rack 1",
            comments="comment1",
            facility_id="rack-1",
            site=cls.sites[0],
            group=cls.rack_groups[0],
            tenant=cls.tenants[0],
            status=cls.rack_status_map["active"],
            role=cls.rackroles[0],
            serial="ABC",
            asset_tag="1001",
            type=RackTypeChoices.TYPE_2POST,
            width=RackWidthChoices.WIDTH_19IN,
            u_height=42,
            desc_units=False,
            outer_width=100,
            outer_depth=100,
            outer_unit=RackDimensionUnitChoices.UNIT_MILLIMETER,
        ),
        Rack.objects.create(
            name="Rack 2",
            comments="comment2",
            facility_id="rack-2",
            site=cls.sites[1],
            group=cls.rack_groups[1],
            tenant=cls.tenants[1],
            status=cls.rack_status_map["planned"],
            role=cls.rackroles[1],
            serial="DEF",
            asset_tag="1002",
            type=RackTypeChoices.TYPE_4POST,
            width=RackWidthChoices.WIDTH_21IN,
            u_height=43,
            desc_units=False,
            outer_width=200,
            outer_depth=200,
            outer_unit=RackDimensionUnitChoices.UNIT_MILLIMETER,
        ),
        Rack.objects.create(
            name="Rack 3",
            comments="comment3",
            facility_id="rack-3",
            site=cls.sites[2],
            group=cls.rack_groups[2],
            tenant=cls.tenants[2],
            status=cls.rack_status_map["reserved"],
            role=cls.rackroles[2],
            serial="GHI",
            asset_tag="1003",
            type=RackTypeChoices.TYPE_CABINET,
            width=RackWidthChoices.WIDTH_23IN,
            u_height=44,
            desc_units=True,
            outer_width=300,
            outer_depth=300,
            outer_unit=RackDimensionUnitChoices.UNIT_INCH,
        ),
    )

    cls.devices = (
        Device.objects.create(
            name="Device 1",
            device_type=device_types[0],
            device_role=device_role,
            rack=cls.racks[0],
            site=cls.sites[0],
            status=device_status_map["active"],
        ),
        Device.objects.create(
            name="Device 2",
            device_type=device_types[1],
            device_role=device_role,
            rack=cls.racks[1],
            site=cls.sites[1],
            status=device_status_map["staged"],
        ),
        Device.objects.create(
            name="Device 3",
            device_type=device_types[2],
            device_role=device_role,
            rack=cls.racks[2],
            site=cls.sites[2],
            status=device_status_map["failed"],
        ),
    )

    cls.prefixes = (
        Prefix.objects.create(prefix=netaddr.IPNetwork("192.168.0.0/16"), site=cls.sites[0]),
        Prefix.objects.create(prefix=netaddr.IPNetwork("192.168.1.0/24"), site=cls.sites[1]),
        Prefix.objects.create(prefix=netaddr.IPNetwork("192.168.2.0/24"), site=cls.sites[2]),
    )

    cls.vlan_groups = (
        VLANGroup.objects.create(name="VLAN Group 1", slug="vlan-group-1", site=cls.sites[0]),
        VLANGroup.objects.create(name="VLAN Group 2", slug="vlan-group-2", site=cls.sites[1]),
        VLANGroup.objects.create(name="VLAN Group 3", slug="vlan-group-3", site=cls.sites[2]),
    )

    cls.vlans = (
        VLAN.objects.create(name="VLAN 101", vid=101, site=cls.sites[0]),
        VLAN.objects.create(name="VLAN 102", vid=102, site=cls.sites[1]),
        VLAN.objects.create(name="VLAN 103", vid=103, site=cls.sites[2]),
    )

    cluster_type = ClusterType.objects.create(name="Cluster Type 1", slug="cluster-type-1")
    cls.clusters = (
        Cluster.objects.create(name="Cluster 1", type=cluster_type, site=cls.sites[0]),
        Cluster.objects.create(name="Cluster 2", type=cluster_type, site=cls.sites[1]),
        Cluster.objects.create(name="Cluster 3", type=cluster_type, site=cls.sites[2]),
    )

    cls.powerfeeds = (
        PowerFeed.objects.create(name="Powerfeed 1", rack=cls.racks[0], power_panel=cls.powerpanels[0]),
        PowerFeed.objects.create(name="Powerfeed 1", rack=cls.racks[1], power_panel=cls.powerpanels[1]),
        PowerFeed.objects.create(name="Powerfeed 1", rack=cls.racks[2], power_panel=cls.powerpanels[2]),
    )

    cls.users = (
        User.objects.create_user(username="TestCaseUser 1"),
        User.objects.create_user(username="TestCaseUser 2"),
        User.objects.create_user(username="TestCaseUser 3"),
    )

    cls.rackreservations = (
        RackReservation.objects.create(
            rack=cls.racks[0],
            units=(1, 2, 3),
            user=cls.users[0],
            description="Rack Reservation 1",
            tenant=cls.tenants[0],
        ),
        RackReservation.objects.create(
            rack=cls.racks[1],
            units=(4, 5, 6),
            user=cls.users[1],
            description="Rack Reservation 2",
            tenant=cls.tenants[1],
        ),
        RackReservation.objects.create(
            rack=cls.racks[2],
            units=(7, 8, 9),
            user=cls.users[2],
            description="Rack Reservation 3",
            tenant=cls.tenants[2],
        ),
    )


class RegionTestCase(FilterTestCases.NameSlugFilterTestCase):
    queryset = Region.objects.all()
    filterset = RegionFilterSet

    @classmethod
    def setUpTestData(cls):
        common_test_data(cls)

        cls.child_regions = (
            Region.objects.create(name="Region 1A", slug="region-1a", parent=cls.regions[0]),
            Region.objects.create(name="Region 1B", slug="region-1b", parent=cls.regions[0]),
            Region.objects.create(name="Region 2A", slug="region-2a", parent=cls.regions[1]),
            Region.objects.create(name="Region 2B", slug="region-2b", parent=cls.regions[1]),
            Region.objects.create(name="Region 3A", slug="region-3a", parent=cls.regions[2]),
            Region.objects.create(name="Region 3B", slug="region-3b", parent=cls.regions[2]),
        )

        Site.objects.create(name="Site 4", slug="site-4", region=cls.regions[2])

    def test_description(self):
        params = {"description": ["A", "B"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent(self):
        parent_regions = Region.objects.filter(parent__isnull=True)[:2]
        params = {"parent_id": [parent_regions[0].pk, parent_regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"parent": [parent_regions[0].slug, parent_regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_children(self):
        params = {"children": [self.child_regions[0].pk, self.child_regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"children": [self.child_regions[1].slug, self.child_regions[2].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_children(self):
        params = {"has_children": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_children": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)

    def test_sites(self):
        sites = Site.objects.filter(region__slug="region-3")
        self.assertEqual(len(sites), 2)
        params = {"sites": [sites[0].pk, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_has_sites(self):
        params = {"has_sites": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_sites": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)


class SiteTestCase(FilterTestCases.NameSlugFilterTestCase):
    queryset = Site.objects.all()
    filterset = SiteFilterSet

    @classmethod
    def setUpTestData(cls):
        common_test_data(cls)

        Site.objects.create(name="Site 4", status=cls.site_status_map["retired"])

    def test_facility(self):
        params = {"facility": ["Facility 1", "Facility 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_asn(self):
        params = {"asn": [65001, 65002]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_latitude(self):
        params = {"latitude": [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_longitude(self):
        params = {"longitude": [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_contact_name(self):
        params = {"contact_name": ["Contact 1", "Contact 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_contact_phone(self):
        params = {"contact_phone": ["123-555-0001", "123-555-0002"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_contact_email(self):
        params = {"contact_email": ["contact1@example.com", "contact2@example.com"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {"status": ["active", "planned"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {"tenant_id": [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"tenant": [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {"tenant_group_id": [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"tenant_group": [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_search(self):
        value = self.queryset.values_list("pk", flat=True)[0]
        params = {"q": value}
        self.assertEqual(self.filterset(params, self.queryset).qs.values_list("pk", flat=True)[0], value)

    def test_comments(self):
        params = {"comments": "COMMENT"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
        params = {"comments": "comment123"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)
        params = {"comments": "comment2"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_circuit_terminations(self):
        circuit_terminations = CircuitTermination.objects.all()[:2]
        params = {"circuit_terminations": [circuit_terminations[0].pk, circuit_terminations[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_circuit_terminations(self):
        params = {"has_circuit_terminations": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_circuit_terminations": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devices(self):
        devices = Device.objects.all()[:2]
        params = {"devices": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_devices(self):
        params = {"has_devices": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_devices": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_powerpanels(self):
        powerpanels = PowerPanel.objects.all()[:2]
        params = {"powerpanels": [powerpanels[0].pk, powerpanels[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_powerpanels(self):
        params = {"has_powerpanels": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_powerpanels": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_rack_groups(self):
        rack_groups = RackGroup.objects.all()[:2]
        params = {"rack_groups": [rack_groups[0].pk, rack_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_rack_groups(self):
        params = {"has_rack_groups": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_rack_groups": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_racks(self):
        racks = Rack.objects.all()[:2]
        params = {"racks": [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_racks(self):
        params = {"has_racks": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_racks": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_prefixes(self):
        prefixes = Prefix.objects.all()[:2]
        params = {"prefixes": [prefixes[0].pk, prefixes[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_prefixes(self):
        params = {"has_prefixes": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_prefixes": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_vlan_groups(self):
        vlan_groups = VLANGroup.objects.all()[:2]
        params = {"vlan_groups": [vlan_groups[0].pk, vlan_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_vlan_groups(self):
        params = {"has_vlan_groups": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_vlan_groups": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_vlans(self):
        vlans = VLAN.objects.all()[:2]
        params = {"vlans": [vlans[0].pk, vlans[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_vlans(self):
        params = {"has_vlans": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_vlans": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_clusters(self):
        clusters = Cluster.objects.all()[:2]
        params = {"clusters": [clusters[0].pk, clusters[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_clusters(self):
        params = {"has_clusters": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_clusters": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_time_zone(self):
        params = {"time_zone": ["America/Los_Angeles", "America/Chicago"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"time_zone": [""]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_physical_address(self):
        params = {"physical_address": "1 road st, albany, ny"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"physical_address": "nomatch"}
        self.assertFalse(self.filterset(params, self.queryset).qs.exists())

    def test_shipping_address(self):
        params = {"shipping_address": "PO Box 1, albany, ny"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"shipping_address": "nomatch"}
        self.assertFalse(self.filterset(params, self.queryset).qs.exists())

    def test_description(self):
        params = {"description": "Site 1 description"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"description": "nomatch"}
        self.assertFalse(self.filterset(params, self.queryset).qs.exists())


class RackGroupTestCase(FilterTestCases.NameSlugFilterTestCase):
    queryset = RackGroup.objects.all()
    filterset = RackGroupFilterSet

    @classmethod
    def setUpTestData(cls):
        common_test_data(cls)

        RackGroup.objects.create(
            name="Child Rack Group 1",
            slug="rack-group-1c",
            site=cls.sites[0],
            parent=cls.rack_groups[0],
            description="A",
        )
        RackGroup.objects.create(
            name="Child Rack Group 2",
            slug="rack-group-2c",
            site=cls.sites[1],
            parent=cls.rack_groups[1],
            description="B",
        )
        RackGroup.objects.create(
            name="Child Rack Group 3",
            slug="rack-group-3c",
            site=cls.sites[2],
            parent=cls.rack_groups[2],
            description="C",
        )
        RackGroup.objects.create(
            name="Rack Group 4",
            slug="rack-group-4",
            site=cls.sites[2],
        )

    def test_description(self):
        params = {"description": ["A", "B"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_site(self):
        sites = Site.objects.filter(slug__in=["site-1", "site-2"])
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_parent(self):
        parent_rack_groups = RackGroup.objects.filter(children__isnull=False)[:2]
        params = {"parent_id": [parent_rack_groups[0].pk, parent_rack_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"parent": [parent_rack_groups[0].slug, parent_rack_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_children(self):
        child_groups = RackGroup.objects.filter(name__startswith="Child").filter(parent__isnull=False)[:2]
        params = {"children": [child_groups[0].pk, child_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        rack_group_4 = RackGroup.objects.filter(slug="rack-group-4").first()
        params = {"children": [rack_group_4.slug, rack_group_4.pk]}
        self.assertFalse(self.filterset(params, self.queryset).qs.exists())

    def test_has_children(self):
        self.assertEqual(self.filterset({"has_children": True}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({"has_children": False}, self.queryset).qs.count(), 4)

    def test_powerpanels(self):
        powerpanels = PowerPanel.objects.all()[:2]
        params = {"powerpanels": [powerpanels[0].pk, powerpanels[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_powerpanels(self):
        self.assertEqual(self.filterset({"has_powerpanels": True}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({"has_powerpanels": False}, self.queryset).qs.count(), 4)

    def test_racks(self):
        racks = Rack.objects.all()[:2]
        params = {"racks": [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_racks(self):
        self.assertEqual(self.filterset({"has_racks": True}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({"has_racks": False}, self.queryset).qs.count(), 4)


class RackRoleTestCase(FilterTestCases.NameSlugFilterTestCase):
    queryset = RackRole.objects.all()
    filterset = RackRoleFilterSet

    @classmethod
    def setUpTestData(cls):
        common_test_data(cls)

        RackRole.objects.create(name="Rack Role 4", slug="rack-role-4", color="abcdef")

    def test_color(self):
        params = {"color": ["ff0000", "00ff00"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_racks(self):
        racks = Rack.objects.all()[:2]
        params = {"racks": [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_racks(self):
        self.assertEqual(self.filterset({"has_racks": True}, self.queryset).qs.count(), 3)
        self.assertEqual(self.filterset({"has_racks": False}, self.queryset).qs.count(), 1)


class RackTestCase(FilterTestCases.FilterTestCase):
    queryset = Rack.objects.all()
    filterset = RackFilterSet

    @classmethod
    def setUpTestData(cls):
        common_test_data(cls)

        Rack.objects.create(
            name="Rack 4",
            facility_id="rack-4",
            site=cls.sites[2],
            group=cls.rack_groups[2],
            tenant=cls.tenants[2],
            status=cls.rack_status_map["active"],
            role=cls.rackroles[2],
            serial="ABCDEF",
            asset_tag="1004",
            type=RackTypeChoices.TYPE_2POST,
            width=RackWidthChoices.WIDTH_19IN,
            u_height=42,
            desc_units=False,
            outer_width=100,
            outer_depth=100,
        )

    def test_name(self):
        params = {"name": ["Rack 1", "Rack 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_facility_id(self):
        params = {"facility_id": ["rack-1", "rack-2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_asset_tag(self):
        params = {"asset_tag": ["1001", "1002"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        params = {"type": [RackTypeChoices.TYPE_2POST, RackTypeChoices.TYPE_4POST]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_width(self):
        params = {"width": [RackWidthChoices.WIDTH_19IN, RackWidthChoices.WIDTH_21IN]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_u_height(self):
        params = {"u_height": [42, 43]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_desc_units(self):
        params = {"desc_units": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"desc_units": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_outer_width(self):
        params = {"outer_width": [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_outer_depth(self):
        params = {"outer_depth": [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_outer_unit(self):
        self.assertEqual(Rack.objects.exclude(outer_unit="").count(), 3)
        params = {"outer_unit": RackDimensionUnitChoices.UNIT_MILLIMETER}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_group(self):
        groups = RackGroup.objects.all()[:2]
        params = {"group_id": [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"group": [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {"status": ["active", "planned"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_role(self):
        roles = RackRole.objects.all()[:2]
        params = {"role_id": [roles[0].pk, roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"role": [roles[0].slug, roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_serial(self):
        params = {"serial": "ABC"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"serial": "abc"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {"tenant_id": [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"tenant": [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {"tenant_group_id": [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"tenant_group": [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_search(self):
        value = self.queryset.values_list("pk", flat=True)[0]
        params = {"q": value}
        self.assertEqual(self.filterset(params, self.queryset).qs.values_list("pk", flat=True)[0], value)

    def test_comments(self):
        rack_1 = Rack.objects.filter(name="Rack 1").first()
        self.assertEqual(self.filterset({"comments": "comment1"}).qs.count(), 1)
        self.assertEqual(self.filterset({"comments": "comment1"}).qs.first().pk, rack_1.pk)

    def test_devices(self):
        devices = Device.objects.all()[:2]
        params = {"devices": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_devices(self):
        params = {"has_devices": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_devices": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_powerfeeds(self):
        powerfeeds = PowerFeed.objects.all()[:2]
        params = {"powerfeeds": [powerfeeds[0], powerfeeds[1]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_powerfeeds(self):
        params = {"has_powerfeeds": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_powerfeeds": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_reservations(self):
        reservations = RackReservation.objects.all()[:2]
        params = {"reservations": [reservations[0], reservations[1]]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_reservations(self):
        params = {"has_reservations": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_reservations": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class RackReservationTestCase(FilterTestCases.FilterTestCase):
    queryset = RackReservation.objects.all()
    filterset = RackReservationFilterSet

    @classmethod
    def setUpTestData(cls):
        common_test_data(cls)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_group(self):
        groups = RackGroup.objects.all()[:2]
        params = {"group_id": [groups[0].pk, groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"group": [groups[0].slug, groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_user(self):
        users = User.objects.filter(username__startswith="TestCaseUser")[:2]
        params = {"user_id": [users[0].pk, users[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"user": [users[0].username, users[1].username]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {"tenant_id": [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"tenant": [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {"tenant_group_id": [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"tenant_group": [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_search(self):
        value = self.queryset.values_list("pk", flat=True)[0]
        params = {"q": value}
        self.assertEqual(self.filterset(params, self.queryset).qs.values_list("pk", flat=True)[0], value)

    def test_description(self):
        params = {"description": "Rack Reservation 1"}
        self.assertSequenceEqual(self.filterset(params, self.queryset).qs.first().units, (1, 2, 3))
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"description": "Rack Reservation 3"}
        self.assertSequenceEqual(self.filterset(params, self.queryset).qs.first().units, (7, 8, 9))
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_rack(self):
        racks = Rack.objects.filter(name__startswith="Rack ")[:2]
        params = {"rack": [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ManufacturerTestCase(FilterTestCases.NameSlugFilterTestCase):
    queryset = Manufacturer.objects.all()
    filterset = ManufacturerFilterSet

    @classmethod
    def setUpTestData(cls):

        Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1", description="A")
        Manufacturer.objects.create(name="Manufacturer 2", slug="manufacturer-2", description="B")
        Manufacturer.objects.create(name="Manufacturer 3", slug="manufacturer-3", description="C")

    def test_description(self):
        params = {"description": ["A", "B"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DeviceTypeTestCase(FilterTestCases.FilterTestCase):
    queryset = DeviceType.objects.all()
    filterset = DeviceTypeFilterSet

    @classmethod
    def setUpTestData(cls):
        common_test_data(cls)

        device_types = DeviceType.objects.all()

        # Add component templates for filtering
        ConsolePortTemplate.objects.create(device_type=device_types[0], name="Console Port 1")
        ConsolePortTemplate.objects.create(device_type=device_types[1], name="Console Port 2")

        ConsoleServerPortTemplate.objects.create(device_type=device_types[0], name="Console Server Port 1")
        ConsoleServerPortTemplate.objects.create(device_type=device_types[1], name="Console Server Port 2")

        PowerPortTemplate.objects.create(device_type=device_types[0], name="Power Port 1")
        PowerPortTemplate.objects.create(device_type=device_types[1], name="Power Port 2")

        PowerOutletTemplate.objects.create(device_type=device_types[0], name="Power Outlet 1")
        PowerOutletTemplate.objects.create(device_type=device_types[1], name="Power Outlet 2")

        InterfaceTemplate.objects.create(device_type=device_types[0], name="Interface 1")
        InterfaceTemplate.objects.create(device_type=device_types[1], name="Interface 2")

        rear_ports = (
            RearPortTemplate.objects.create(
                device_type=device_types[0],
                name="Rear Port 1",
                type=PortTypeChoices.TYPE_8P8C,
            ),
            RearPortTemplate.objects.create(
                device_type=device_types[1],
                name="Rear Port 2",
                type=PortTypeChoices.TYPE_8P8C,
            ),
        )

        FrontPortTemplate.objects.create(
            device_type=device_types[0],
            name="Front Port 1",
            type=PortTypeChoices.TYPE_8P8C,
            rear_port=rear_ports[0],
        )
        FrontPortTemplate.objects.create(
            device_type=device_types[1],
            name="Front Port 2",
            type=PortTypeChoices.TYPE_8P8C,
            rear_port=rear_ports[1],
        )

        DeviceBayTemplate.objects.create(device_type=device_types[0], name="Device Bay 1")
        DeviceBayTemplate.objects.create(device_type=device_types[1], name="Device Bay 2")

    def test_model(self):
        params = {"model": ["Model 1", "Model 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {"slug": ["model-1", "model-2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_part_number(self):
        params = {"part_number": ["Part Number 1", "Part Number 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_u_height(self):
        params = {"u_height": [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_is_full_depth(self):
        params = {"is_full_depth": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"is_full_depth": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_subdevice_role(self):
        params = {"subdevice_role": SubdeviceRoleChoices.ROLE_PARENT}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {"manufacturer_id": [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"manufacturer": [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_console_ports(self):
        params = {"console_ports": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"console_ports": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_console_server_ports(self):
        params = {"console_server_ports": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"console_server_ports": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_power_ports(self):
        params = {"power_ports": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"power_ports": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_power_outlets(self):
        params = {"power_outlets": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"power_outlets": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_interfaces(self):
        params = {"interfaces": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"interfaces": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_pass_through_ports(self):
        params = {"pass_through_ports": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"pass_through_ports": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_bays(self):
        params = {"device_bays": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"device_bays": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_search(self):
        value = self.queryset.values_list("pk", flat=True)[0]
        params = {"q": value}
        self.assertEqual(self.filterset(params, self.queryset).qs.values_list("pk", flat=True)[0], value)

    def test_comments(self):
        params = {"comments": ["Device type 1", "Device type 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_instances(self):
        instances = Device.objects.all()[:2]
        params = {"instances": [instances[0].pk, instances[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_instances(self):
        params = {"has_instances": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"has_instances": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_consoleport_templates(self):
        consoleport_templates = ConsolePortTemplate.objects.all()[:2]
        params = {"consoleport_templates": [consoleport_templates[0].pk, consoleport_templates[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_consoleport_templates(self):
        params = {"has_consoleport_templates": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_consoleport_templates": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_consoleserverport_templates(self):
        csp_templates = ConsoleServerPortTemplate.objects.all()[:2]
        params = {"consoleserverport_templates": [csp_templates[0].pk, csp_templates[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_consoleserverport_templates(self):
        params = {"has_consoleserverport_templates": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_consoleserverport_templates": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_powerport_templates(self):
        powerport_templates = PowerPortTemplate.objects.all()[:2]
        params = {"powerport_templates": [powerport_templates[0].pk, powerport_templates[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_powerport_templates(self):
        params = {"has_powerport_templates": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_powerport_templates": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_poweroutlet_templates(self):
        poweroutlet_templates = PowerOutletTemplate.objects.all()[:2]
        params = {"poweroutlet_templates": [poweroutlet_templates[0].pk, poweroutlet_templates[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_poweroutlet_templates(self):
        params = {"has_poweroutlet_templates": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_poweroutlet_templates": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_interface_templates(self):
        interface_templates = InterfaceTemplate.objects.all()[:2]
        params = {"interface_templates": [interface_templates[0].pk, interface_templates[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_interface_templates(self):
        params = {"has_interface_templates": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_interface_templates": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_frontport_templates(self):
        frontport_templates = FrontPortTemplate.objects.all()[:2]
        params = {"frontport_templates": [frontport_templates[0].pk, frontport_templates[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_frontport_templates(self):
        params = {"has_frontport_templates": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_frontport_templates": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_rearport_templates(self):
        rearport_templates = RearPortTemplate.objects.all()[:2]
        params = {"rearport_templates": [rearport_templates[0].pk, rearport_templates[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_rearport_templates(self):
        params = {"has_rearport_templates": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_rearport_templates": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_devicebay_templates(self):
        devicebay_templates = DeviceBayTemplate.objects.all()[:2]
        params = {"devicebay_templates": [devicebay_templates[0].pk, devicebay_templates[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_has_devicebay_templates(self):
        params = {"has_devicebay_templates": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_devicebay_templates": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class ConsolePortTemplateTestCase(FilterTestCases.FilterTestCase):
    queryset = ConsolePortTemplate.objects.all()
    filterset = ConsolePortTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")

        device_types = (
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 2", slug="model-2"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 3", slug="model-3"),
        )

        ConsolePortTemplate.objects.create(device_type=device_types[0], name="Console Port 1")
        ConsolePortTemplate.objects.create(device_type=device_types[1], name="Console Port 2")
        ConsolePortTemplate.objects.create(device_type=device_types[2], name="Console Port 3")

    def test_name(self):
        params = {"name": ["Console Port 1", "Console Port 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {"devicetype_id": [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class ConsoleServerPortTemplateTestCase(FilterTestCases.FilterTestCase):
    queryset = ConsoleServerPortTemplate.objects.all()
    filterset = ConsoleServerPortTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")

        device_types = (
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 2", slug="model-2"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 3", slug="model-3"),
        )

        ConsoleServerPortTemplate.objects.create(device_type=device_types[0], name="Console Server Port 1")
        ConsoleServerPortTemplate.objects.create(device_type=device_types[1], name="Console Server Port 2")
        ConsoleServerPortTemplate.objects.create(device_type=device_types[2], name="Console Server Port 3")

    def test_name(self):
        params = {"name": ["Console Server Port 1", "Console Server Port 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {"devicetype_id": [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class PowerPortTemplateTestCase(FilterTestCases.FilterTestCase):
    queryset = PowerPortTemplate.objects.all()
    filterset = PowerPortTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")

        device_types = (
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 2", slug="model-2"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 3", slug="model-3"),
        )

        PowerPortTemplate.objects.create(
            device_type=device_types[0],
            name="Power Port 1",
            maximum_draw=100,
            allocated_draw=50,
        )
        PowerPortTemplate.objects.create(
            device_type=device_types[1],
            name="Power Port 2",
            maximum_draw=200,
            allocated_draw=100,
        )
        PowerPortTemplate.objects.create(
            device_type=device_types[2],
            name="Power Port 3",
            maximum_draw=300,
            allocated_draw=150,
        )

    def test_name(self):
        params = {"name": ["Power Port 1", "Power Port 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {"devicetype_id": [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_maximum_draw(self):
        params = {"maximum_draw": [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_allocated_draw(self):
        params = {"allocated_draw": [50, 100]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class PowerOutletTemplateTestCase(FilterTestCases.FilterTestCase):
    queryset = PowerOutletTemplate.objects.all()
    filterset = PowerOutletTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")

        device_types = (
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 2", slug="model-2"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 3", slug="model-3"),
        )

        PowerOutletTemplate.objects.create(
            device_type=device_types[0],
            name="Power Outlet 1",
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A,
        )
        PowerOutletTemplate.objects.create(
            device_type=device_types[1],
            name="Power Outlet 2",
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_B,
        )
        PowerOutletTemplate.objects.create(
            device_type=device_types[2],
            name="Power Outlet 3",
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_C,
        )

    def test_name(self):
        params = {"name": ["Power Outlet 1", "Power Outlet 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {"devicetype_id": [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_feed_leg(self):
        # TODO: Support filtering for multiple values
        params = {"feed_leg": PowerOutletFeedLegChoices.FEED_LEG_A}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class InterfaceTemplateTestCase(FilterTestCases.FilterTestCase):
    queryset = InterfaceTemplate.objects.all()
    filterset = InterfaceTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")

        device_types = (
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 2", slug="model-2"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 3", slug="model-3"),
        )

        InterfaceTemplate.objects.create(
            device_type=device_types[0],
            name="Interface 1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            mgmt_only=True,
        )
        InterfaceTemplate.objects.create(
            device_type=device_types[1],
            name="Interface 2",
            type=InterfaceTypeChoices.TYPE_1GE_GBIC,
            mgmt_only=False,
        )
        InterfaceTemplate.objects.create(
            device_type=device_types[2],
            name="Interface 3",
            type=InterfaceTypeChoices.TYPE_1GE_SFP,
            mgmt_only=False,
        )

    def test_name(self):
        params = {"name": ["Interface 1", "Interface 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {"devicetype_id": [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        # TODO: Support filtering for multiple values
        params = {"type": InterfaceTypeChoices.TYPE_1GE_FIXED}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_mgmt_only(self):
        params = {"mgmt_only": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"mgmt_only": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class FrontPortTemplateTestCase(FilterTestCases.FilterTestCase):
    queryset = FrontPortTemplate.objects.all()
    filterset = FrontPortTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")

        device_types = (
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 2", slug="model-2"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 3", slug="model-3"),
        )

        rear_ports = (
            RearPortTemplate.objects.create(
                device_type=device_types[0],
                name="Rear Port 1",
                type=PortTypeChoices.TYPE_8P8C,
            ),
            RearPortTemplate.objects.create(
                device_type=device_types[1],
                name="Rear Port 2",
                type=PortTypeChoices.TYPE_8P8C,
            ),
            RearPortTemplate.objects.create(
                device_type=device_types[2],
                name="Rear Port 3",
                type=PortTypeChoices.TYPE_8P8C,
            ),
        )

        FrontPortTemplate.objects.create(
            device_type=device_types[0],
            name="Front Port 1",
            rear_port=rear_ports[0],
            type=PortTypeChoices.TYPE_8P8C,
        )
        FrontPortTemplate.objects.create(
            device_type=device_types[1],
            name="Front Port 2",
            rear_port=rear_ports[1],
            type=PortTypeChoices.TYPE_110_PUNCH,
        )
        FrontPortTemplate.objects.create(
            device_type=device_types[2],
            name="Front Port 3",
            rear_port=rear_ports[2],
            type=PortTypeChoices.TYPE_BNC,
        )

    def test_name(self):
        params = {"name": ["Front Port 1", "Front Port 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {"devicetype_id": [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        # TODO: Support filtering for multiple values
        params = {"type": PortTypeChoices.TYPE_8P8C}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class RearPortTemplateTestCase(FilterTestCases.FilterTestCase):
    queryset = RearPortTemplate.objects.all()
    filterset = RearPortTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")

        device_types = (
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 2", slug="model-2"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 3", slug="model-3"),
        )

        RearPortTemplate.objects.create(
            device_type=device_types[0],
            name="Rear Port 1",
            type=PortTypeChoices.TYPE_8P8C,
            positions=1,
        )
        RearPortTemplate.objects.create(
            device_type=device_types[1],
            name="Rear Port 2",
            type=PortTypeChoices.TYPE_110_PUNCH,
            positions=2,
        )
        RearPortTemplate.objects.create(
            device_type=device_types[2],
            name="Rear Port 3",
            type=PortTypeChoices.TYPE_BNC,
            positions=3,
        )

    def test_name(self):
        params = {"name": ["Rear Port 1", "Rear Port 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {"devicetype_id": [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        # TODO: Support filtering for multiple values
        params = {"type": PortTypeChoices.TYPE_8P8C}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_positions(self):
        params = {"positions": [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DeviceBayTemplateTestCase(FilterTestCases.FilterTestCase):
    queryset = DeviceBayTemplate.objects.all()
    filterset = DeviceBayTemplateFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")

        device_types = (
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 2", slug="model-2"),
            DeviceType.objects.create(manufacturer=manufacturer, model="Model 3", slug="model-3"),
        )

        DeviceBayTemplate.objects.create(device_type=device_types[0], name="Device Bay 1")
        DeviceBayTemplate.objects.create(device_type=device_types[1], name="Device Bay 2")
        DeviceBayTemplate.objects.create(device_type=device_types[2], name="Device Bay 3")

    def test_name(self):
        params = {"name": ["Device Bay 1", "Device Bay 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devicetype_id(self):
        device_types = DeviceType.objects.all()[:2]
        params = {"devicetype_id": [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DeviceRoleTestCase(FilterTestCases.NameSlugFilterTestCase):
    queryset = DeviceRole.objects.all()
    filterset = DeviceRoleFilterSet

    @classmethod
    def setUpTestData(cls):

        DeviceRole.objects.create(name="Device Role 1", slug="device-role-1", color="ff0000", vm_role=True)
        DeviceRole.objects.create(name="Device Role 2", slug="device-role-2", color="00ff00", vm_role=True)
        DeviceRole.objects.create(
            name="Device Role 3",
            slug="device-role-3",
            color="0000ff",
            vm_role=False,
        )

    def test_color(self):
        params = {"color": ["ff0000", "00ff00"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vm_role(self):
        params = {"vm_role": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"vm_role": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class PlatformTestCase(FilterTestCases.NameSlugFilterTestCase):
    queryset = Platform.objects.all()
    filterset = PlatformFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1"),
            Manufacturer.objects.create(name="Manufacturer 2", slug="manufacturer-2"),
            Manufacturer.objects.create(name="Manufacturer 3", slug="manufacturer-3"),
        )

        Platform.objects.create(
            name="Platform 1",
            slug="platform-1",
            manufacturer=manufacturers[0],
            napalm_driver="driver-1",
            description="A",
        )
        Platform.objects.create(
            name="Platform 2",
            slug="platform-2",
            manufacturer=manufacturers[1],
            napalm_driver="driver-2",
            description="B",
        )
        Platform.objects.create(
            name="Platform 3",
            slug="platform-3",
            manufacturer=manufacturers[2],
            napalm_driver="driver-3",
            description="C",
        )

    def test_description(self):
        params = {"description": ["A", "B"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_napalm_driver(self):
        params = {"napalm_driver": ["driver-1", "driver-2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {"manufacturer_id": [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"manufacturer": [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DeviceTestCase(FilterTestCases.FilterTestCase):
    queryset = Device.objects.all()
    filterset = DeviceFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1"),
            Manufacturer.objects.create(name="Manufacturer 2", slug="manufacturer-2"),
            Manufacturer.objects.create(name="Manufacturer 3", slug="manufacturer-3"),
        )

        device_types = (
            DeviceType.objects.create(
                manufacturer=manufacturers[0],
                model="Model 1",
                slug="model-1",
                is_full_depth=True,
            ),
            DeviceType.objects.create(
                manufacturer=manufacturers[1],
                model="Model 2",
                slug="model-2",
                is_full_depth=True,
            ),
            DeviceType.objects.create(
                manufacturer=manufacturers[2],
                model="Model 3",
                slug="model-3",
                is_full_depth=False,
            ),
        )

        device_roles = (
            DeviceRole.objects.create(name="Device Role 1", slug="device-role-1"),
            DeviceRole.objects.create(name="Device Role 2", slug="device-role-2"),
            DeviceRole.objects.create(name="Device Role 3", slug="device-role-3"),
        )

        device_statuses = Status.objects.get_for_model(Device)
        device_status_map = {ds.slug: ds for ds in device_statuses.all()}

        platforms = (
            Platform.objects.create(name="Platform 1", slug="platform-1"),
            Platform.objects.create(name="Platform 2", slug="platform-2"),
            Platform.objects.create(name="Platform 3", slug="platform-3"),
        )

        regions = (
            Region.objects.create(name="Region 1", slug="region-1"),
            Region.objects.create(name="Region 2", slug="region-2"),
            Region.objects.create(name="Region 3", slug="region-3"),
        )

        sites = (
            Site.objects.create(name="Site 1", slug="site-1", region=regions[0]),
            Site.objects.create(name="Site 2", slug="site-2", region=regions[1]),
            Site.objects.create(name="Site 3", slug="site-3", region=regions[2]),
        )

        rack_groups = (
            RackGroup.objects.create(name="Rack Group 1", slug="rack-group-1", site=sites[0]),
            RackGroup.objects.create(name="Rack Group 2", slug="rack-group-2", site=sites[1]),
            RackGroup.objects.create(name="Rack Group 3", slug="rack-group-3", site=sites[2]),
        )

        racks = (
            Rack.objects.create(name="Rack 1", site=sites[0], group=rack_groups[0]),
            Rack.objects.create(name="Rack 2", site=sites[1], group=rack_groups[1]),
            Rack.objects.create(name="Rack 3", site=sites[2], group=rack_groups[2]),
        )

        cluster_type = ClusterType.objects.create(name="Cluster Type 1", slug="cluster-type-1")
        clusters = (
            Cluster.objects.create(name="Cluster 1", type=cluster_type),
            Cluster.objects.create(name="Cluster 2", type=cluster_type),
            Cluster.objects.create(name="Cluster 3", type=cluster_type),
        )

        secrets_groups = (
            SecretsGroup.objects.create(name="Secrets group 1", slug="secrets-group-1"),
            SecretsGroup.objects.create(name="Secrets group 2", slug="secrets-group-2"),
            SecretsGroup.objects.create(name="Secrets group 3", slug="secrets-group-3"),
        )

        tenant_groups = (
            TenantGroup.objects.create(name="Tenant group 1", slug="tenant-group-1"),
            TenantGroup.objects.create(name="Tenant group 2", slug="tenant-group-2"),
            TenantGroup.objects.create(name="Tenant group 3", slug="tenant-group-3"),
        )

        tenants = (
            Tenant.objects.create(name="Tenant 1", slug="tenant-1", group=tenant_groups[0]),
            Tenant.objects.create(name="Tenant 2", slug="tenant-2", group=tenant_groups[1]),
            Tenant.objects.create(name="Tenant 3", slug="tenant-3", group=tenant_groups[2]),
        )

        devices = (
            Device.objects.create(
                name="Device 1",
                device_type=device_types[0],
                device_role=device_roles[0],
                platform=platforms[0],
                tenant=tenants[0],
                serial="ABC",
                asset_tag="1001",
                site=sites[0],
                rack=racks[0],
                position=1,
                face=DeviceFaceChoices.FACE_FRONT,
                status=device_status_map["active"],
                cluster=clusters[0],
                secrets_group=secrets_groups[0],
                local_context_data={"foo": 123},
            ),
            Device.objects.create(
                name="Device 2",
                device_type=device_types[1],
                device_role=device_roles[1],
                platform=platforms[1],
                tenant=tenants[1],
                serial="DEF",
                asset_tag="1002",
                site=sites[1],
                rack=racks[1],
                position=2,
                face=DeviceFaceChoices.FACE_FRONT,
                status=device_status_map["staged"],
                cluster=clusters[1],
                secrets_group=secrets_groups[1],
            ),
            Device.objects.create(
                name="Device 3",
                device_type=device_types[2],
                device_role=device_roles[2],
                platform=platforms[2],
                tenant=tenants[2],
                serial="GHI",
                asset_tag="1003",
                site=sites[2],
                rack=racks[2],
                position=3,
                face=DeviceFaceChoices.FACE_REAR,
                status=device_status_map["failed"],
                cluster=clusters[2],
                secrets_group=secrets_groups[2],
            ),
        )

        # Add components for filtering
        ConsolePort.objects.create(device=devices[0], name="Console Port 1"),
        ConsolePort.objects.create(device=devices[1], name="Console Port 2"),

        ConsoleServerPort.objects.create(device=devices[0], name="Console Server Port 1"),
        ConsoleServerPort.objects.create(device=devices[1], name="Console Server Port 2"),

        PowerPort.objects.create(device=devices[0], name="Power Port 1"),
        PowerPort.objects.create(device=devices[1], name="Power Port 2"),

        PowerOutlet.objects.create(device=devices[0], name="Power Outlet 1"),
        PowerOutlet.objects.create(device=devices[1], name="Power Outlet 2"),

        interfaces = (
            Interface.objects.create(device=devices[0], name="Interface 1", mac_address="00-00-00-00-00-01"),
            Interface.objects.create(device=devices[1], name="Interface 2", mac_address="00-00-00-00-00-02"),
        )

        rear_ports = (
            RearPort.objects.create(device=devices[0], name="Rear Port 1", type=PortTypeChoices.TYPE_8P8C),
            RearPort.objects.create(device=devices[1], name="Rear Port 2", type=PortTypeChoices.TYPE_8P8C),
        )

        FrontPort.objects.create(
            device=devices[0],
            name="Front Port 1",
            type=PortTypeChoices.TYPE_8P8C,
            rear_port=rear_ports[0],
        ),
        FrontPort.objects.create(
            device=devices[1],
            name="Front Port 2",
            type=PortTypeChoices.TYPE_8P8C,
            rear_port=rear_ports[1],
        ),

        DeviceBay.objects.create(device=devices[0], name="Device Bay 1"),
        DeviceBay.objects.create(device=devices[1], name="Device Bay 2"),

        # Assign primary IPs for filtering

        ipaddresses = (
            IPAddress.objects.create(address="192.0.2.1/24", assigned_object=interfaces[0]),
            IPAddress.objects.create(address="192.0.2.2/24", assigned_object=interfaces[1]),
        )

        Device.objects.filter(pk=devices[0].pk).update(primary_ip4=ipaddresses[0])
        Device.objects.filter(pk=devices[1].pk).update(primary_ip4=ipaddresses[1])

        # VirtualChassis assignment for filtering
        virtual_chassis = VirtualChassis.objects.create(master=devices[0])
        Device.objects.filter(pk=devices[0].pk).update(virtual_chassis=virtual_chassis, vc_position=1, vc_priority=1)
        Device.objects.filter(pk=devices[1].pk).update(virtual_chassis=virtual_chassis, vc_position=2, vc_priority=2)

    def test_name(self):
        params = {"name": ["Device 1", "Device 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_asset_tag(self):
        params = {"asset_tag": ["1001", "1002"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_face(self):
        params = {"face": DeviceFaceChoices.FACE_FRONT}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_position(self):
        params = {"position": [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vc_position(self):
        params = {"vc_position": [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vc_priority(self):
        params = {"vc_priority": [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {"manufacturer_id": [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"manufacturer": [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devicetype(self):
        device_types = DeviceType.objects.all()[:2]
        params = {"device_type_id": [device_types[0].pk, device_types[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_devicerole(self):
        device_roles = DeviceRole.objects.all()[:2]
        params = {"role_id": [device_roles[0].pk, device_roles[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"role": [device_roles[0].slug, device_roles[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_platform(self):
        platforms = Platform.objects.all()[:2]
        params = {"platform_id": [platforms[0].pk, platforms[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"platform": [platforms[0].slug, platforms[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_secrets_group(self):
        secrets_groups = SecretsGroup.objects.all()[:2]
        params = {"secrets_group_id": [secrets_groups[0].pk, secrets_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"secrets_group": [secrets_groups[0].slug, secrets_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rackgroup(self):
        rack_groups = RackGroup.objects.all()[:2]
        params = {"rack_group_id": [rack_groups[0].pk, rack_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {"rack_id": [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cluster(self):
        clusters = Cluster.objects.all()[:2]
        params = {"cluster_id": [clusters[0].pk, clusters[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_model(self):
        params = {"model": ["model-1", "model-2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {"status": ["active", "staged"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_is_full_depth(self):
        params = {"is_full_depth": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"is_full_depth": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_mac_address(self):
        params = {"mac_address": ["00-00-00-00-00-01", "00-00-00-00-00-02"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_serial(self):
        params = {"serial": "ABC"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"serial": "abc"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_has_primary_ip(self):
        params = {"has_primary_ip": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_primary_ip": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_virtual_chassis_id(self):
        params = {"virtual_chassis_id": [VirtualChassis.objects.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_virtual_chassis_member(self):
        params = {"virtual_chassis_member": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"virtual_chassis_member": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_is_virtual_chassis_member(self):
        params = {"is_virtual_chassis_member": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"is_virtual_chassis_member": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_console_ports(self):
        params = {"console_ports": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"console_ports": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_has_console_ports(self):
        params = {"has_console_ports": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_console_ports": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_console_server_ports(self):
        params = {"console_server_ports": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"console_server_ports": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_has_console_server_ports(self):
        params = {"has_console_server_ports": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_console_server_ports": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_power_ports(self):
        params = {"power_ports": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"power_ports": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_has_power_ports(self):
        params = {"has_power_ports": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_power_ports": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_power_outlets(self):
        params = {"power_outlets": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"power_outlets": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_has_power_outlets(self):
        params = {"has_power_outlets": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_power_outlets": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_interfaces(self):
        params = {"interfaces": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"interfaces": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_has_interfaces(self):
        params = {"has_interfaces": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_interfaces": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_pass_through_ports(self):
        params = {"pass_through_ports": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"pass_through_ports": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_has_front_ports(self):
        params = {"has_front_ports": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_front_ports": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_has_rear_ports(self):
        params = {"has_rear_ports": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_rear_ports": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_device_bays(self):
        params = {"device_bays": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"device_bays": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_has_device_bays(self):
        params = {"has_device_bays": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"has_device_bays": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_local_context_data(self):
        params = {"local_context_data": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"local_context_data": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant(self):
        tenants = Tenant.objects.all()[:2]
        params = {"tenant_id": [tenants[0].pk, tenants[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"tenant": [tenants[0].slug, tenants[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_tenant_group(self):
        tenant_groups = TenantGroup.objects.all()[:2]
        params = {"tenant_group_id": [tenant_groups[0].pk, tenant_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"tenant_group": [tenant_groups[0].slug, tenant_groups[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_search(self):
        value = self.queryset.values_list("pk", flat=True)[0]
        params = {"q": value}
        self.assertEqual(self.filterset(params, self.queryset).qs.values_list("pk", flat=True)[0], value)


class ConsolePortTestCase(FilterTestCases.FilterTestCase):
    queryset = ConsolePort.objects.all()
    filterset = ConsolePortFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region.objects.create(name="Region 1", slug="region-1"),
            Region.objects.create(name="Region 2", slug="region-2"),
            Region.objects.create(name="Region 3", slug="region-3"),
        )

        sites = (
            Site.objects.create(name="Site 1", slug="site-1", region=regions[0]),
            Site.objects.create(name="Site 2", slug="site-2", region=regions[1]),
            Site.objects.create(name="Site 3", slug="site-3", region=regions[2]),
            Site.objects.create(name="Site X", slug="site-x"),
        )
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        devices = (
            Device.objects.create(
                name="Device 1",
                device_type=device_type,
                device_role=device_role,
                site=sites[0],
            ),
            Device.objects.create(
                name="Device 2",
                device_type=device_type,
                device_role=device_role,
                site=sites[1],
            ),
            Device.objects.create(
                name="Device 3",
                device_type=device_type,
                device_role=device_role,
                site=sites[2],
            ),
            Device.objects.create(
                name=None,
                device_type=device_type,
                device_role=device_role,
                site=sites[3],
            ),  # For cable connections
        )

        console_server_ports = (
            ConsoleServerPort.objects.create(device=devices[3], name="Console Server Port 1"),
            ConsoleServerPort.objects.create(device=devices[3], name="Console Server Port 2"),
        )

        console_ports = (
            ConsolePort.objects.create(device=devices[0], name="Console Port 1", description="First"),
            ConsolePort.objects.create(device=devices[1], name="Console Port 2", description="Second"),
            ConsolePort.objects.create(device=devices[2], name="Console Port 3", description="Third"),
        )

        cable_statuses = Status.objects.get_for_model(Cable)
        status_connected = cable_statuses.get(slug="connected")

        # Cables
        Cable.objects.create(
            termination_a=console_ports[0],
            termination_b=console_server_ports[0],
            status=status_connected,
        )
        Cable.objects.create(
            termination_a=console_ports[1],
            termination_b=console_server_ports[1],
            status=status_connected,
        )
        # Third port is not connected

    def test_name(self):
        params = {"name": ["Console Port 1", "Console Port 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {"description": ["First", "Second"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_connected(self):
        params = {"connected": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"connected": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = [
            Device.objects.get(name="Device 1"),
            Device.objects.get(name="Device 2"),
        ]
        params = {"device_id": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"device": [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {"cabled": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"cabled": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class ConsoleServerPortTestCase(FilterTestCases.FilterTestCase):
    queryset = ConsoleServerPort.objects.all()
    filterset = ConsoleServerPortFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region.objects.create(name="Region 1", slug="region-1"),
            Region.objects.create(name="Region 2", slug="region-2"),
            Region.objects.create(name="Region 3", slug="region-3"),
        )

        sites = (
            Site.objects.create(name="Site 1", slug="site-1", region=regions[0]),
            Site.objects.create(name="Site 2", slug="site-2", region=regions[1]),
            Site.objects.create(name="Site 3", slug="site-3", region=regions[2]),
            Site.objects.create(name="Site X", slug="site-x"),
        )
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        devices = (
            Device.objects.create(
                name="Device 1",
                device_type=device_type,
                device_role=device_role,
                site=sites[0],
            ),
            Device.objects.create(
                name="Device 2",
                device_type=device_type,
                device_role=device_role,
                site=sites[1],
            ),
            Device.objects.create(
                name="Device 3",
                device_type=device_type,
                device_role=device_role,
                site=sites[2],
            ),
            Device.objects.create(
                name=None,
                device_type=device_type,
                device_role=device_role,
                site=sites[3],
            ),  # For cable connections
        )

        console_ports = (
            ConsolePort.objects.create(device=devices[3], name="Console Server Port 1"),
            ConsolePort.objects.create(device=devices[3], name="Console Server Port 2"),
        )

        console_server_ports = (
            ConsoleServerPort.objects.create(device=devices[0], name="Console Server Port 1", description="First"),
            ConsoleServerPort.objects.create(device=devices[1], name="Console Server Port 2", description="Second"),
            ConsoleServerPort.objects.create(device=devices[2], name="Console Server Port 3", description="Third"),
        )

        cable_statuses = Status.objects.get_for_model(Cable)
        status_connected = cable_statuses.get(slug="connected")

        # Cables
        Cable.objects.create(
            termination_a=console_server_ports[0],
            termination_b=console_ports[0],
            status=status_connected,
        )
        Cable.objects.create(
            termination_a=console_server_ports[1],
            termination_b=console_ports[1],
            status=status_connected,
        )
        # Third port is not connected

    def test_name(self):
        params = {"name": ["Console Server Port 1", "Console Server Port 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {"description": ["First", "Second"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_connected(self):
        params = {"connected": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"connected": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = [
            Device.objects.get(name="Device 1"),
            Device.objects.get(name="Device 2"),
        ]
        params = {"device_id": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"device": [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {"cabled": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"cabled": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class PowerPortTestCase(FilterTestCases.FilterTestCase):
    queryset = PowerPort.objects.all()
    filterset = PowerPortFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region.objects.create(name="Region 1", slug="region-1"),
            Region.objects.create(name="Region 2", slug="region-2"),
            Region.objects.create(name="Region 3", slug="region-3"),
        )

        sites = (
            Site.objects.create(name="Site 1", slug="site-1", region=regions[0]),
            Site.objects.create(name="Site 2", slug="site-2", region=regions[1]),
            Site.objects.create(name="Site 3", slug="site-3", region=regions[2]),
            Site.objects.create(name="Site X", slug="site-x"),
        )
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        devices = (
            Device.objects.create(
                name="Device 1",
                device_type=device_type,
                device_role=device_role,
                site=sites[0],
            ),
            Device.objects.create(
                name="Device 2",
                device_type=device_type,
                device_role=device_role,
                site=sites[1],
            ),
            Device.objects.create(
                name="Device 3",
                device_type=device_type,
                device_role=device_role,
                site=sites[2],
            ),
            Device.objects.create(
                name=None,
                device_type=device_type,
                device_role=device_role,
                site=sites[3],
            ),  # For cable connections
        )

        power_outlets = (
            PowerOutlet.objects.create(device=devices[3], name="Power Outlet 1"),
            PowerOutlet.objects.create(device=devices[3], name="Power Outlet 2"),
        )

        power_ports = (
            PowerPort.objects.create(
                device=devices[0],
                name="Power Port 1",
                maximum_draw=100,
                allocated_draw=50,
                description="First",
            ),
            PowerPort.objects.create(
                device=devices[1],
                name="Power Port 2",
                maximum_draw=200,
                allocated_draw=100,
                description="Second",
            ),
            PowerPort.objects.create(
                device=devices[2],
                name="Power Port 3",
                maximum_draw=300,
                allocated_draw=150,
                description="Third",
            ),
        )

        cable_statuses = Status.objects.get_for_model(Cable)
        status_connected = cable_statuses.get(slug="connected")

        # Cables
        Cable.objects.create(
            termination_a=power_ports[0],
            termination_b=power_outlets[0],
            status=status_connected,
        )
        Cable.objects.create(
            termination_a=power_ports[1],
            termination_b=power_outlets[1],
            status=status_connected,
        )
        # Third port is not connected

    def test_name(self):
        params = {"name": ["Power Port 1", "Power Port 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {"description": ["First", "Second"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_maximum_draw(self):
        params = {"maximum_draw": [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_allocated_draw(self):
        params = {"allocated_draw": [50, 100]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_connected(self):
        params = {"connected": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"connected": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = [
            Device.objects.get(name="Device 1"),
            Device.objects.get(name="Device 2"),
        ]
        params = {"device_id": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"device": [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {"cabled": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"cabled": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class PowerOutletTestCase(FilterTestCases.FilterTestCase):
    queryset = PowerOutlet.objects.all()
    filterset = PowerOutletFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region.objects.create(name="Region 1", slug="region-1"),
            Region.objects.create(name="Region 2", slug="region-2"),
            Region.objects.create(name="Region 3", slug="region-3"),
        )

        sites = (
            Site.objects.create(name="Site 1", slug="site-1", region=regions[0]),
            Site.objects.create(name="Site 2", slug="site-2", region=regions[1]),
            Site.objects.create(name="Site 3", slug="site-3", region=regions[2]),
            Site.objects.create(name="Site X", slug="site-x"),
        )
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        devices = (
            Device.objects.create(
                name="Device 1",
                device_type=device_type,
                device_role=device_role,
                site=sites[0],
            ),
            Device.objects.create(
                name="Device 2",
                device_type=device_type,
                device_role=device_role,
                site=sites[1],
            ),
            Device.objects.create(
                name="Device 3",
                device_type=device_type,
                device_role=device_role,
                site=sites[2],
            ),
            Device.objects.create(
                name=None,
                device_type=device_type,
                device_role=device_role,
                site=sites[3],
            ),  # For cable connections
        )

        power_ports = (
            PowerPort.objects.create(device=devices[3], name="Power Outlet 1"),
            PowerPort.objects.create(device=devices[3], name="Power Outlet 2"),
        )

        power_outlets = (
            PowerOutlet.objects.create(
                device=devices[0],
                name="Power Outlet 1",
                feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A,
                description="First",
            ),
            PowerOutlet.objects.create(
                device=devices[1],
                name="Power Outlet 2",
                feed_leg=PowerOutletFeedLegChoices.FEED_LEG_B,
                description="Second",
            ),
            PowerOutlet.objects.create(
                device=devices[2],
                name="Power Outlet 3",
                feed_leg=PowerOutletFeedLegChoices.FEED_LEG_C,
                description="Third",
            ),
        )

        cable_statuses = Status.objects.get_for_model(Cable)
        status_connected = cable_statuses.get(slug="connected")

        # Cables
        Cable.objects.create(
            termination_a=power_outlets[0],
            termination_b=power_ports[0],
            status=status_connected,
        )
        Cable.objects.create(
            termination_a=power_outlets[1],
            termination_b=power_ports[1],
            status=status_connected,
        )
        # Third port is not connected

    def test_name(self):
        params = {"name": ["Power Outlet 1", "Power Outlet 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {"description": ["First", "Second"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_feed_leg(self):
        # TODO: Support filtering for multiple values
        params = {"feed_leg": PowerOutletFeedLegChoices.FEED_LEG_A}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_connected(self):
        params = {"connected": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"connected": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = [
            Device.objects.get(name="Device 1"),
            Device.objects.get(name="Device 2"),
        ]
        params = {"device_id": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"device": [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {"cabled": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"cabled": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class InterfaceTestCase(FilterTestCases.FilterTestCase):
    queryset = Interface.objects.all()
    filterset = InterfaceFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region.objects.create(name="Region 1", slug="region-1"),
            Region.objects.create(name="Region 2", slug="region-2"),
            Region.objects.create(name="Region 3", slug="region-3"),
        )

        sites = (
            Site.objects.create(name="Site 1", slug="site-1", region=regions[0]),
            Site.objects.create(name="Site 2", slug="site-2", region=regions[1]),
            Site.objects.create(name="Site 3", slug="site-3", region=regions[2]),
            Site.objects.create(name="Site X", slug="site-x"),
        )
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        devices = (
            Device.objects.create(
                name="Device 1",
                device_type=device_type,
                device_role=device_role,
                site=sites[0],
            ),
            Device.objects.create(
                name="Device 2",
                device_type=device_type,
                device_role=device_role,
                site=sites[1],
            ),
            Device.objects.create(
                name="Device 3",
                device_type=device_type,
                device_role=device_role,
                site=sites[2],
            ),
            Device.objects.create(
                name=None,
                device_type=device_type,
                device_role=device_role,
                site=sites[3],
            ),  # For cable connections
        )

        vlan1 = VLAN.objects.create(name="VLAN 1", vid=1)
        vlan2 = VLAN.objects.create(name="VLAN 2", vid=2)
        vlan3 = VLAN.objects.create(name="VLAN 3", vid=3)

        statuses = Status.objects.get_for_model(Interface)

        interfaces = (
            Interface.objects.create(
                device=devices[0],
                name="Interface 1",
                type=InterfaceTypeChoices.TYPE_1GE_SFP,
                enabled=True,
                mgmt_only=True,
                mtu=100,
                mode=InterfaceModeChoices.MODE_ACCESS,
                mac_address="00-00-00-00-00-01",
                untagged_vlan=vlan1,
                description="First",
                status=statuses.get(slug="active"),
            ),
            Interface.objects.create(
                device=devices[1],
                name="Interface 2",
                type=InterfaceTypeChoices.TYPE_1GE_GBIC,
                enabled=True,
                mgmt_only=True,
                mtu=200,
                mode=InterfaceModeChoices.MODE_TAGGED,
                mac_address="00-00-00-00-00-02",
                untagged_vlan=vlan2,
                description="Second",
                status=statuses.get(slug="planned"),
            ),
            Interface.objects.create(
                device=devices[2],
                name="Interface 3",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
                enabled=False,
                mgmt_only=False,
                mtu=300,
                mode=InterfaceModeChoices.MODE_TAGGED_ALL,
                mac_address="00-00-00-00-00-03",
                description="Third",
                status=statuses.get(slug="failed"),
            ),
            Interface.objects.create(
                device=devices[3],
                name="Interface 4",
                type=InterfaceTypeChoices.TYPE_OTHER,
                enabled=True,
                mgmt_only=True,
                status=statuses.get(slug="failed"),
            ),
            Interface.objects.create(
                device=devices[3],
                name="Interface 5",
                type=InterfaceTypeChoices.TYPE_OTHER,
                enabled=True,
                mgmt_only=True,
                status=statuses.get(slug="planned"),
            ),
            Interface.objects.create(
                device=devices[3],
                name="Interface 6",
                type=InterfaceTypeChoices.TYPE_OTHER,
                enabled=False,
                mgmt_only=False,
                status=statuses.get(slug="active"),
            ),
        )

        # Tagged VLAN interface is "Interface 6"
        tagged_interface = interfaces[-1]
        tagged_interface.tagged_vlans.add(vlan3)

        cable_statuses = Status.objects.get_for_model(Cable)
        status_connected = cable_statuses.get(slug="connected")

        # Cables
        Cable.objects.create(
            termination_a=interfaces[0],
            termination_b=interfaces[3],
            status=status_connected,
        )
        Cable.objects.create(
            termination_a=interfaces[1],
            termination_b=interfaces[4],
            status=status_connected,
        )
        # Third pair is not connected

    def test_name(self):
        params = {"name": ["Interface 1", "Interface 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_connected(self):
        params = {"connected": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"connected": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_enabled(self):
        params = {"enabled": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"enabled": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_mtu(self):
        params = {"mtu": [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_mgmt_only(self):
        params = {"mgmt_only": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"mgmt_only": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_mode(self):
        params = {"mode": InterfaceModeChoices.MODE_ACCESS}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {"description": ["First", "Second"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent(self):
        # Create child interfaces
        parent_interface = Interface.objects.first()
        child_interfaces = (
            Interface(
                device=parent_interface.device,
                name="Child 1",
                parent_interface=parent_interface,
                type=InterfaceTypeChoices.TYPE_VIRTUAL,
            ),
            Interface(
                device=parent_interface.device,
                name="Child 2",
                parent_interface=parent_interface,
                type=InterfaceTypeChoices.TYPE_VIRTUAL,
            ),
            Interface(
                device=parent_interface.device,
                name="Child 3",
                parent_interface=parent_interface,
                type=InterfaceTypeChoices.TYPE_VIRTUAL,
            ),
        )
        Interface.objects.bulk_create(child_interfaces)

        params = {"parent_interface_id": [parent_interface.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_bridge(self):
        # Create bridged interfaces
        device = Interface.objects.first().device
        bridge_interface = Interface.objects.create(
            device=device,
            name="Bridge 1",
            type=InterfaceTypeChoices.TYPE_BRIDGE,
        )
        bridged_interfaces = (
            Interface(
                device=bridge_interface.device,
                name="Bridged 1",
                bridge=bridge_interface,
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface(
                device=bridge_interface.device,
                name="Bridged 2",
                bridge=bridge_interface,
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface(
                device=bridge_interface.device,
                name="Bridged 3",
                bridge=bridge_interface,
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
        )
        Interface.objects.bulk_create(bridged_interfaces)

        params = {"bridge_id": [bridge_interface.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_lag(self):
        # Create LAG members
        device = Device.objects.first()
        lag_interface = Interface(device=device, name="LAG", type=InterfaceTypeChoices.TYPE_LAG)
        lag_interface.save()
        lag_members = (
            Interface(device=device, name="Member 1", lag=lag_interface, type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=device, name="Member 2", lag=lag_interface, type=InterfaceTypeChoices.TYPE_1GE_FIXED),
            Interface(device=device, name="Member 3", lag=lag_interface, type=InterfaceTypeChoices.TYPE_1GE_FIXED),
        )
        Interface.objects.bulk_create(lag_members)

        params = {"lag_id": [lag_interface.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_device_with_common_vc(self):
        """Assert only interfaces belonging to devices with common VC are returned"""
        site = Site.objects.first()
        device_type = DeviceType.objects.first()
        device_role = DeviceRole.objects.first()
        devices = (
            Device.objects.create(
                name="Device in vc 1",
                device_type=device_type,
                device_role=device_role,
                site=site,
            ),
            Device.objects.create(
                name="Device in vc 2",
                device_type=device_type,
                device_role=device_role,
                site=site,
            ),
            Device.objects.create(
                name="Device not in vc",
                device_type=device_type,
                device_role=device_role,
                site=site,
            ),
        )

        # VirtualChassis assignment for filtering
        virtual_chassis = VirtualChassis.objects.create(master=devices[0])
        Device.objects.filter(pk=devices[0].pk).update(virtual_chassis=virtual_chassis, vc_position=1, vc_priority=1)
        Device.objects.filter(pk=devices[1].pk).update(virtual_chassis=virtual_chassis, vc_position=2, vc_priority=2)

        Interface.objects.create(device=devices[0], name="int1")
        Interface.objects.create(device=devices[0], name="int2")
        Interface.objects.create(device=devices[1], name="int3")
        Interface.objects.create(device=devices[2], name="int4")

        params = {"device_with_common_vc": devices[0].pk}
        queryset = self.filterset(params, self.queryset).qs
        self.assertEqual(queryset.count(), 3)
        # Assert interface of a device belonging to same VC as device[0] are returned
        self.assertTrue(queryset.filter(name="int3").exists())
        # Assert interface of a device not belonging as device[0] to same VC are not returned
        self.assertFalse(queryset.filter(name="int4").exists())

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = [
            Device.objects.get(name="Device 1"),
            Device.objects.get(name="Device 2"),
        ]
        params = {"device_id": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"device": [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {"cabled": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"cabled": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_kind(self):
        params = {"kind": "physical"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 6)
        params = {"kind": "virtual"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 0)

    def test_mac_address(self):
        params = {"mac_address": ["00-00-00-00-00-01", "00-00-00-00-00-02"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        params = {
            "type": [
                InterfaceTypeChoices.TYPE_1GE_FIXED,
                InterfaceTypeChoices.TYPE_1GE_GBIC,
            ]
        }
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_vlan(self):
        params = {"vlan": VLAN.objects.first().vid}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_vlan_id(self):
        params = {"vlan_id": VLAN.objects.last().id}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_status(self):
        params = {"status": ["active", "failed"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class FrontPortTestCase(FilterTestCases.FilterTestCase):
    queryset = FrontPort.objects.all()
    filterset = FrontPortFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region.objects.create(name="Region 1", slug="region-1"),
            Region.objects.create(name="Region 2", slug="region-2"),
            Region.objects.create(name="Region 3", slug="region-3"),
        )

        sites = (
            Site.objects.create(name="Site 1", slug="site-1", region=regions[0]),
            Site.objects.create(name="Site 2", slug="site-2", region=regions[1]),
            Site.objects.create(name="Site 3", slug="site-3", region=regions[2]),
            Site.objects.create(name="Site X", slug="site-x"),
        )
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        devices = (
            Device.objects.create(
                name="Device 1",
                device_type=device_type,
                device_role=device_role,
                site=sites[0],
            ),
            Device.objects.create(
                name="Device 2",
                device_type=device_type,
                device_role=device_role,
                site=sites[1],
            ),
            Device.objects.create(
                name="Device 3",
                device_type=device_type,
                device_role=device_role,
                site=sites[2],
            ),
            Device.objects.create(
                name=None,
                device_type=device_type,
                device_role=device_role,
                site=sites[3],
            ),  # For cable connections
        )

        rear_ports = (
            RearPort.objects.create(
                device=devices[0],
                name="Rear Port 1",
                type=PortTypeChoices.TYPE_8P8C,
                positions=6,
            ),
            RearPort.objects.create(
                device=devices[1],
                name="Rear Port 2",
                type=PortTypeChoices.TYPE_8P8C,
                positions=6,
            ),
            RearPort.objects.create(
                device=devices[2],
                name="Rear Port 3",
                type=PortTypeChoices.TYPE_8P8C,
                positions=6,
            ),
            RearPort.objects.create(
                device=devices[3],
                name="Rear Port 4",
                type=PortTypeChoices.TYPE_8P8C,
                positions=6,
            ),
            RearPort.objects.create(
                device=devices[3],
                name="Rear Port 5",
                type=PortTypeChoices.TYPE_8P8C,
                positions=6,
            ),
            RearPort.objects.create(
                device=devices[3],
                name="Rear Port 6",
                type=PortTypeChoices.TYPE_8P8C,
                positions=6,
            ),
        )

        front_ports = (
            FrontPort.objects.create(
                device=devices[0],
                name="Front Port 1",
                type=PortTypeChoices.TYPE_8P8C,
                rear_port=rear_ports[0],
                rear_port_position=1,
                description="First",
            ),
            FrontPort.objects.create(
                device=devices[1],
                name="Front Port 2",
                type=PortTypeChoices.TYPE_110_PUNCH,
                rear_port=rear_ports[1],
                rear_port_position=2,
                description="Second",
            ),
            FrontPort.objects.create(
                device=devices[2],
                name="Front Port 3",
                type=PortTypeChoices.TYPE_BNC,
                rear_port=rear_ports[2],
                rear_port_position=3,
                description="Third",
            ),
            FrontPort.objects.create(
                device=devices[3],
                name="Front Port 4",
                type=PortTypeChoices.TYPE_FC,
                rear_port=rear_ports[3],
                rear_port_position=1,
            ),
            FrontPort.objects.create(
                device=devices[3],
                name="Front Port 5",
                type=PortTypeChoices.TYPE_FC,
                rear_port=rear_ports[4],
                rear_port_position=1,
            ),
            FrontPort.objects.create(
                device=devices[3],
                name="Front Port 6",
                type=PortTypeChoices.TYPE_FC,
                rear_port=rear_ports[5],
                rear_port_position=1,
            ),
        )

        cable_statuses = Status.objects.get_for_model(Cable)
        status_connected = cable_statuses.get(slug="connected")

        # Cables
        Cable.objects.create(
            termination_a=front_ports[0],
            termination_b=front_ports[3],
            status=status_connected,
        )
        Cable.objects.create(
            termination_a=front_ports[1],
            termination_b=front_ports[4],
            status=status_connected,
        )
        # Third port is not connected

    def test_name(self):
        params = {"name": ["Front Port 1", "Front Port 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        # TODO: Test for multiple values
        params = {"type": PortTypeChoices.TYPE_8P8C}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_description(self):
        params = {"description": ["First", "Second"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = [
            Device.objects.get(name="Device 1"),
            Device.objects.get(name="Device 2"),
        ]
        params = {"device_id": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"device": [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {"cabled": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"cabled": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class RearPortTestCase(FilterTestCases.FilterTestCase):
    queryset = RearPort.objects.all()
    filterset = RearPortFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region.objects.create(name="Region 1", slug="region-1"),
            Region.objects.create(name="Region 2", slug="region-2"),
            Region.objects.create(name="Region 3", slug="region-3"),
        )

        sites = (
            Site.objects.create(name="Site 1", slug="site-1", region=regions[0]),
            Site.objects.create(name="Site 2", slug="site-2", region=regions[1]),
            Site.objects.create(name="Site 3", slug="site-3", region=regions[2]),
            Site.objects.create(name="Site X", slug="site-x"),
        )
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        devices = (
            Device.objects.create(
                name="Device 1",
                device_type=device_type,
                device_role=device_role,
                site=sites[0],
            ),
            Device.objects.create(
                name="Device 2",
                device_type=device_type,
                device_role=device_role,
                site=sites[1],
            ),
            Device.objects.create(
                name="Device 3",
                device_type=device_type,
                device_role=device_role,
                site=sites[2],
            ),
            Device.objects.create(
                name=None,
                device_type=device_type,
                device_role=device_role,
                site=sites[3],
            ),  # For cable connections
        )

        rear_ports = (
            RearPort.objects.create(
                device=devices[0],
                name="Rear Port 1",
                type=PortTypeChoices.TYPE_8P8C,
                positions=1,
                description="First",
            ),
            RearPort.objects.create(
                device=devices[1],
                name="Rear Port 2",
                type=PortTypeChoices.TYPE_110_PUNCH,
                positions=2,
                description="Second",
            ),
            RearPort.objects.create(
                device=devices[2],
                name="Rear Port 3",
                type=PortTypeChoices.TYPE_BNC,
                positions=3,
                description="Third",
            ),
            RearPort.objects.create(
                device=devices[3],
                name="Rear Port 4",
                type=PortTypeChoices.TYPE_FC,
                positions=4,
            ),
            RearPort.objects.create(
                device=devices[3],
                name="Rear Port 5",
                type=PortTypeChoices.TYPE_FC,
                positions=5,
            ),
            RearPort.objects.create(
                device=devices[3],
                name="Rear Port 6",
                type=PortTypeChoices.TYPE_FC,
                positions=6,
            ),
        )

        cable_statuses = Status.objects.get_for_model(Cable)
        status_connected = cable_statuses.get(slug="connected")

        # Cables
        Cable.objects.create(
            termination_a=rear_ports[0],
            termination_b=rear_ports[3],
            status=status_connected,
        )
        Cable.objects.create(
            termination_a=rear_ports[1],
            termination_b=rear_ports[4],
            status=status_connected,
        )
        # Third port is not connected

    def test_name(self):
        params = {"name": ["Rear Port 1", "Rear Port 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        # TODO: Test for multiple values
        params = {"type": PortTypeChoices.TYPE_8P8C}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_positions(self):
        params = {"positions": [1, 2]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {"description": ["First", "Second"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = [
            Device.objects.get(name="Device 1"),
            Device.objects.get(name="Device 2"),
        ]
        params = {"device_id": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"device": [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {"cabled": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"cabled": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class DeviceBayTestCase(FilterTestCases.FilterTestCase):
    queryset = DeviceBay.objects.all()
    filterset = DeviceBayFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region.objects.create(name="Region 1", slug="region-1"),
            Region.objects.create(name="Region 2", slug="region-2"),
            Region.objects.create(name="Region 3", slug="region-3"),
        )

        sites = (
            Site.objects.create(name="Site 1", slug="site-1", region=regions[0]),
            Site.objects.create(name="Site 2", slug="site-2", region=regions[1]),
            Site.objects.create(name="Site 3", slug="site-3", region=regions[2]),
            Site.objects.create(name="Site X", slug="site-x"),
        )
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        devices = (
            Device.objects.create(
                name="Device 1",
                device_type=device_type,
                device_role=device_role,
                site=sites[0],
            ),
            Device.objects.create(
                name="Device 2",
                device_type=device_type,
                device_role=device_role,
                site=sites[1],
            ),
            Device.objects.create(
                name="Device 3",
                device_type=device_type,
                device_role=device_role,
                site=sites[2],
            ),
        )

        DeviceBay.objects.create(device=devices[0], name="Device Bay 1", description="First")
        DeviceBay.objects.create(device=devices[1], name="Device Bay 2", description="Second")
        DeviceBay.objects.create(device=devices[2], name="Device Bay 3", description="Third")

    def test_name(self):
        params = {"name": ["Device Bay 1", "Device Bay 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_description(self):
        params = {"description": ["First", "Second"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_device(self):
        devices = [
            Device.objects.get(name="Device 1"),
            Device.objects.get(name="Device 2"),
        ]
        params = {"device_id": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"device": [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class InventoryItemTestCase(FilterTestCases.FilterTestCase):
    queryset = InventoryItem.objects.all()
    filterset = InventoryItemFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturers = (
            Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1"),
            Manufacturer.objects.create(name="Manufacturer 2", slug="manufacturer-2"),
            Manufacturer.objects.create(name="Manufacturer 3", slug="manufacturer-3"),
        )

        device_type = DeviceType.objects.create(manufacturer=manufacturers[0], model="Model 1", slug="model-1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        regions = (
            Region.objects.create(name="Region 1", slug="region-1"),
            Region.objects.create(name="Region 2", slug="region-2"),
            Region.objects.create(name="Region 3", slug="region-3"),
        )

        sites = (
            Site.objects.create(name="Site 1", slug="site-1", region=regions[0]),
            Site.objects.create(name="Site 2", slug="site-2", region=regions[1]),
            Site.objects.create(name="Site 3", slug="site-3", region=regions[2]),
        )

        devices = (
            Device.objects.create(
                name="Device 1",
                device_type=device_type,
                device_role=device_role,
                site=sites[0],
            ),
            Device.objects.create(
                name="Device 2",
                device_type=device_type,
                device_role=device_role,
                site=sites[1],
            ),
            Device.objects.create(
                name="Device 3",
                device_type=device_type,
                device_role=device_role,
                site=sites[2],
            ),
        )

        inventory_items = (
            InventoryItem.objects.create(
                device=devices[0],
                manufacturer=manufacturers[0],
                name="Inventory Item 1",
                part_id="1001",
                serial="ABC",
                asset_tag="1001",
                discovered=True,
                description="First",
            ),
            InventoryItem.objects.create(
                device=devices[1],
                manufacturer=manufacturers[1],
                name="Inventory Item 2",
                part_id="1002",
                serial="DEF",
                asset_tag="1002",
                discovered=True,
                description="Second",
            ),
            InventoryItem.objects.create(
                device=devices[2],
                manufacturer=manufacturers[2],
                name="Inventory Item 3",
                part_id="1003",
                serial="GHI",
                asset_tag="1003",
                discovered=False,
                description="Third",
            ),
        )

        InventoryItem.objects.create(device=devices[0], name="Inventory Item 1A", parent=inventory_items[0])
        InventoryItem.objects.create(device=devices[1], name="Inventory Item 2A", parent=inventory_items[1])
        InventoryItem.objects.create(device=devices[2], name="Inventory Item 3A", parent=inventory_items[2])

    def test_name(self):
        params = {"name": ["Inventory Item 1", "Inventory Item 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_part_id(self):
        params = {"part_id": ["1001", "1002"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_asset_tag(self):
        params = {"asset_tag": ["1001", "1002"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_discovered(self):
        # TODO: Fix boolean value
        params = {"discovered": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"discovered": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_device(self):
        # TODO: Allow multiple values
        device = Device.objects.first()
        params = {"device_id": device.pk}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"device": device.name}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_parent_id(self):
        parent_items = InventoryItem.objects.filter(parent__isnull=True)[:2]
        params = {"parent_id": [parent_items[0].pk, parent_items[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_manufacturer(self):
        manufacturers = Manufacturer.objects.all()[:2]
        params = {"manufacturer_id": [manufacturers[0].pk, manufacturers[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"manufacturer": [manufacturers[0].slug, manufacturers[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_serial(self):
        params = {"serial": "ABC"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)
        params = {"serial": "abc"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_search(self):
        value = self.queryset.values_list("pk", flat=True)[0]
        params = {"q": value}
        self.assertEqual(self.filterset(params, self.queryset).qs.values_list("pk", flat=True)[0], value)


class VirtualChassisTestCase(FilterTestCases.FilterTestCase):
    queryset = VirtualChassis.objects.all()
    filterset = VirtualChassisFilterSet

    @classmethod
    def setUpTestData(cls):

        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        regions = (
            Region.objects.create(name="Region 1", slug="region-1"),
            Region.objects.create(name="Region 2", slug="region-2"),
            Region.objects.create(name="Region 3", slug="region-3"),
        )

        sites = (
            Site.objects.create(name="Site 1", slug="site-1", region=regions[0]),
            Site.objects.create(name="Site 2", slug="site-2", region=regions[1]),
            Site.objects.create(name="Site 3", slug="site-3", region=regions[2]),
        )

        devices = (
            Device.objects.create(
                name="Device 1",
                device_type=device_type,
                device_role=device_role,
                site=sites[0],
                vc_position=1,
            ),
            Device.objects.create(
                name="Device 2",
                device_type=device_type,
                device_role=device_role,
                site=sites[0],
                vc_position=2,
            ),
            Device.objects.create(
                name="Device 3",
                device_type=device_type,
                device_role=device_role,
                site=sites[1],
                vc_position=1,
            ),
            Device.objects.create(
                name="Device 4",
                device_type=device_type,
                device_role=device_role,
                site=sites[1],
                vc_position=2,
            ),
            Device.objects.create(
                name="Device 5",
                device_type=device_type,
                device_role=device_role,
                site=sites[2],
                vc_position=1,
            ),
            Device.objects.create(
                name="Device 6",
                device_type=device_type,
                device_role=device_role,
                site=sites[2],
                vc_position=2,
            ),
        )

        virtual_chassis = (
            VirtualChassis.objects.create(name="VC 1", master=devices[0], domain="Domain 1"),
            VirtualChassis.objects.create(name="VC 2", master=devices[2], domain="Domain 2"),
            VirtualChassis.objects.create(name="VC 3", master=devices[4], domain="Domain 3"),
        )

        Device.objects.filter(pk=devices[1].pk).update(virtual_chassis=virtual_chassis[0])
        Device.objects.filter(pk=devices[3].pk).update(virtual_chassis=virtual_chassis[1])
        Device.objects.filter(pk=devices[5].pk).update(virtual_chassis=virtual_chassis[2])

    def test_domain(self):
        params = {"domain": ["Domain 1", "Domain 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_master(self):
        masters = Device.objects.all()
        params = {"master_id": [masters[0].pk, masters[2].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"master": [masters[0].name, masters[2].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_name(self):
        params = {"name": ["VC 1", "VC 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_search(self):
        value = self.queryset.values_list("pk", flat=True)[0]
        params = {"q": value}
        self.assertEqual(self.filterset(params, self.queryset).qs.values_list("pk", flat=True)[0], value)


class CableTestCase(FilterTestCases.FilterTestCase):
    queryset = Cable.objects.all()
    filterset = CableFilterSet

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site.objects.create(name="Site 1", slug="site-1"),
            Site.objects.create(name="Site 2", slug="site-2"),
            Site.objects.create(name="Site 3", slug="site-3"),
        )

        tenants = (
            Tenant.objects.create(name="Tenant 1", slug="tenant-1"),
            Tenant.objects.create(name="Tenant 2", slug="tenant-2"),
        )

        racks = (
            Rack.objects.create(name="Rack 1", site=sites[0]),
            Rack.objects.create(name="Rack 2", site=sites[1]),
            Rack.objects.create(name="Rack 3", site=sites[2]),
        )

        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Model 1", slug="model-1")
        device_role = DeviceRole.objects.create(name="Device Role 1", slug="device-role-1")

        devices = (
            Device.objects.create(
                name="Device 1",
                device_type=device_type,
                device_role=device_role,
                site=sites[0],
                rack=racks[0],
                position=1,
                tenant=tenants[0],
            ),
            Device.objects.create(
                name="Device 2",
                device_type=device_type,
                device_role=device_role,
                site=sites[0],
                rack=racks[0],
                position=2,
                tenant=tenants[0],
            ),
            Device.objects.create(
                name="Device 3",
                device_type=device_type,
                device_role=device_role,
                site=sites[1],
                rack=racks[1],
                position=1,
                tenant=tenants[1],
            ),
            Device.objects.create(
                name="Device 4",
                device_type=device_type,
                device_role=device_role,
                site=sites[1],
                rack=racks[1],
                position=2,
            ),
            Device.objects.create(
                name="Device 5",
                device_type=device_type,
                device_role=device_role,
                site=sites[2],
                rack=racks[2],
                position=1,
            ),
            Device.objects.create(
                name="Device 6",
                device_type=device_type,
                device_role=device_role,
                site=sites[2],
                rack=racks[2],
                position=2,
            ),
        )

        interfaces = (
            Interface.objects.create(
                device=devices[0],
                name="Interface 1",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface.objects.create(
                device=devices[0],
                name="Interface 2",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface.objects.create(
                device=devices[1],
                name="Interface 3",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface.objects.create(
                device=devices[1],
                name="Interface 4",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface.objects.create(
                device=devices[2],
                name="Interface 5",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface.objects.create(
                device=devices[2],
                name="Interface 6",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface.objects.create(
                device=devices[3],
                name="Interface 7",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface.objects.create(
                device=devices[3],
                name="Interface 8",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface.objects.create(
                device=devices[4],
                name="Interface 9",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface.objects.create(
                device=devices[4],
                name="Interface 10",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface.objects.create(
                device=devices[5],
                name="Interface 11",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface.objects.create(
                device=devices[5],
                name="Interface 12",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
        )

        statuses = Status.objects.get_for_model(Cable)
        cls.status_connected = statuses.get(slug="connected")
        cls.status_planned = statuses.get(slug="planned")

        # Cables
        Cable.objects.create(
            termination_a=interfaces[1],
            termination_b=interfaces[2],
            label="Cable 1",
            type=CableTypeChoices.TYPE_CAT3,
            status=cls.status_connected,
            color="aa1409",
            length=10,
            length_unit=CableLengthUnitChoices.UNIT_FOOT,
        )
        Cable.objects.create(
            termination_a=interfaces[3],
            termination_b=interfaces[4],
            label="Cable 2",
            type=CableTypeChoices.TYPE_CAT3,
            status=cls.status_connected,
            color="aa1409",
            length=20,
            length_unit=CableLengthUnitChoices.UNIT_FOOT,
        )
        Cable.objects.create(
            termination_a=interfaces[5],
            termination_b=interfaces[6],
            label="Cable 3",
            type=CableTypeChoices.TYPE_CAT5E,
            status=cls.status_connected,
            color="f44336",
            length=30,
            length_unit=CableLengthUnitChoices.UNIT_FOOT,
        )
        Cable.objects.create(
            termination_a=interfaces[7],
            termination_b=interfaces[8],
            label="Cable 4",
            type=CableTypeChoices.TYPE_CAT5E,
            status=cls.status_planned,
            color="f44336",
            length=40,
            length_unit=CableLengthUnitChoices.UNIT_FOOT,
        )
        Cable.objects.create(
            termination_a=interfaces[9],
            termination_b=interfaces[10],
            label="Cable 5",
            type=CableTypeChoices.TYPE_CAT6,
            status=cls.status_planned,
            color="e91e63",
            length=10,
            length_unit=CableLengthUnitChoices.UNIT_METER,
        )
        Cable.objects.create(
            termination_a=interfaces[11],
            termination_b=interfaces[0],
            label="Cable 6",
            type=CableTypeChoices.TYPE_CAT6,
            status=cls.status_planned,
            color="e91e63",
            length=20,
            length_unit=CableLengthUnitChoices.UNIT_METER,
        )

    def test_label(self):
        params = {"label": ["Cable 1", "Cable 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_length(self):
        params = {"length": [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_length_unit(self):
        params = {"length_unit": CableLengthUnitChoices.UNIT_FOOT}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_type(self):
        params = {"type": [CableTypeChoices.TYPE_CAT3, CableTypeChoices.TYPE_CAT5E]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_status(self):
        params = {"status": ["connected"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"status": ["planned"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_color(self):
        params = {"color": ["aa1409", "f44336"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_device(self):
        devices = [
            Device.objects.get(name="Device 1"),
            Device.objects.get(name="Device 2"),
        ]
        params = {"device_id": [devices[0].pk, devices[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {"device": [devices[0].name, devices[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_rack(self):
        racks = Rack.objects.all()[:2]
        params = {"rack_id": [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
        params = {"rack": [racks[0].name, racks[1].name]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_site(self):
        site = Site.objects.all()[:2]
        params = {"site_id": [site[0].pk, site[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)
        params = {"site": [site[0].slug, site[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 5)

    def test_tenant(self):
        tenant = Tenant.objects.all()[:2]
        params = {"tenant_id": [tenant[0].pk, tenant[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {"tenant": [tenant[0].slug, tenant[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)


class PowerPanelTestCase(FilterTestCases.FilterTestCase):
    queryset = PowerPanel.objects.all()
    filterset = PowerPanelFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region.objects.create(name="Region 1", slug="region-1"),
            Region.objects.create(name="Region 2", slug="region-2"),
            Region.objects.create(name="Region 3", slug="region-3"),
        )

        sites = (
            Site.objects.create(name="Site 1", slug="site-1", region=regions[0]),
            Site.objects.create(name="Site 2", slug="site-2", region=regions[1]),
            Site.objects.create(name="Site 3", slug="site-3", region=regions[2]),
        )

        rack_groups = (
            RackGroup.objects.create(name="Rack Group 1", slug="rack-group-1", site=sites[0]),
            RackGroup.objects.create(name="Rack Group 2", slug="rack-group-2", site=sites[1]),
            RackGroup.objects.create(name="Rack Group 3", slug="rack-group-3", site=sites[2]),
        )

        PowerPanel.objects.create(name="Power Panel 1", site=sites[0], rack_group=rack_groups[0]),
        PowerPanel.objects.create(name="Power Panel 2", site=sites[1], rack_group=rack_groups[1]),
        PowerPanel.objects.create(name="Power Panel 3", site=sites[2], rack_group=rack_groups[2]),

    def test_name(self):
        params = {"name": ["Power Panel 1", "Power Panel 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack_group(self):
        rack_groups = RackGroup.objects.all()[:2]
        params = {"rack_group_id": [rack_groups[0].pk, rack_groups[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class PowerFeedTestCase(FilterTestCases.FilterTestCase):
    queryset = PowerFeed.objects.all()
    filterset = PowerFeedFilterSet

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region.objects.create(name="Region 1", slug="region-1"),
            Region.objects.create(name="Region 2", slug="region-2"),
            Region.objects.create(name="Region 3", slug="region-3"),
        )

        sites = (
            Site.objects.create(name="Site 1", slug="site-1", region=regions[0]),
            Site.objects.create(name="Site 2", slug="site-2", region=regions[1]),
            Site.objects.create(name="Site 3", slug="site-3", region=regions[2]),
        )

        racks = (
            Rack.objects.create(name="Rack 1", site=sites[0]),
            Rack.objects.create(name="Rack 2", site=sites[1]),
            Rack.objects.create(name="Rack 3", site=sites[2]),
        )

        power_panels = (
            PowerPanel.objects.create(name="Power Panel 1", site=sites[0]),
            PowerPanel.objects.create(name="Power Panel 2", site=sites[1]),
            PowerPanel.objects.create(name="Power Panel 3", site=sites[2]),
        )

        pf_statuses = Status.objects.get_for_model(PowerFeed)
        pf_status_map = {s.slug: s for s in pf_statuses.all()}

        power_feeds = (
            PowerFeed.objects.create(
                power_panel=power_panels[0],
                rack=racks[0],
                name="Power Feed 1",
                status=pf_status_map["active"],
                type=PowerFeedTypeChoices.TYPE_PRIMARY,
                supply=PowerFeedSupplyChoices.SUPPLY_AC,
                phase=PowerFeedPhaseChoices.PHASE_3PHASE,
                voltage=100,
                amperage=100,
                max_utilization=10,
            ),
            PowerFeed.objects.create(
                power_panel=power_panels[1],
                rack=racks[1],
                name="Power Feed 2",
                status=pf_status_map["failed"],
                type=PowerFeedTypeChoices.TYPE_PRIMARY,
                supply=PowerFeedSupplyChoices.SUPPLY_AC,
                phase=PowerFeedPhaseChoices.PHASE_3PHASE,
                voltage=200,
                amperage=200,
                max_utilization=20,
            ),
            PowerFeed.objects.create(
                power_panel=power_panels[2],
                rack=racks[2],
                name="Power Feed 3",
                status=pf_status_map["offline"],
                type=PowerFeedTypeChoices.TYPE_REDUNDANT,
                supply=PowerFeedSupplyChoices.SUPPLY_DC,
                phase=PowerFeedPhaseChoices.PHASE_SINGLE,
                voltage=300,
                amperage=300,
                max_utilization=30,
            ),
        )

        manufacturer = Manufacturer.objects.create(name="Manufacturer", slug="manufacturer")
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="Model", slug="model")
        device_role = DeviceRole.objects.create(name="Device Role", slug="device-role")
        device = Device.objects.create(
            name="Device",
            device_type=device_type,
            device_role=device_role,
            site=sites[0],
        )
        power_ports = (
            PowerPort.objects.create(device=device, name="Power Port 1"),
            PowerPort.objects.create(device=device, name="Power Port 2"),
        )

        cable_statuses = Status.objects.get_for_model(Cable)
        status_connected = cable_statuses.get(slug="connected")

        Cable.objects.create(
            termination_a=power_feeds[0],
            termination_b=power_ports[0],
            status=status_connected,
        )
        Cable.objects.create(
            termination_a=power_feeds[1],
            termination_b=power_ports[1],
            status=status_connected,
        )

    def test_name(self):
        params = {"name": ["Power Feed 1", "Power Feed 2"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_status(self):
        params = {"status": ["active", "offline"]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_type(self):
        params = {"type": PowerFeedTypeChoices.TYPE_PRIMARY}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_supply(self):
        params = {"supply": PowerFeedSupplyChoices.SUPPLY_AC}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_phase(self):
        params = {"phase": PowerFeedPhaseChoices.PHASE_3PHASE}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_voltage(self):
        params = {"voltage": [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_amperage(self):
        params = {"amperage": [100, 200]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_max_utilization(self):
        params = {"max_utilization": [10, 20]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {"region_id": [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"region": [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {"site_id": [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"site": [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_power_panel_id(self):
        power_panels = PowerPanel.objects.all()[:2]
        params = {"power_panel_id": [power_panels[0].pk, power_panels[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_rack_id(self):
        racks = Rack.objects.all()[:2]
        params = {"rack_id": [racks[0].pk, racks[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_cabled(self):
        params = {"cabled": "true"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"cabled": "false"}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_connected(self):
        params = {"connected": True}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {"connected": False}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


# TODO: Connection filters
