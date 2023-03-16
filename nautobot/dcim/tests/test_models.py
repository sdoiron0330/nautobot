from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.test import TestCase

from nautobot.circuits.models import Circuit, CircuitTermination, CircuitType, Provider, ProviderNetwork
from nautobot.dcim.choices import (
    CableStatusChoices,
    CableTypeChoices,
    DeviceFaceChoices,
    InterfaceModeChoices,
    InterfaceTypeChoices,
    PortTypeChoices,
    PowerOutletFeedLegChoices,
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
    DeviceRedundancyGroup,
    DeviceType,
    FrontPort,
    FrontPortTemplate,
    Interface,
    InterfaceTemplate,
    Location,
    LocationType,
    Manufacturer,
    PowerPort,
    PowerPortTemplate,
    PowerOutlet,
    PowerOutletTemplate,
    PowerPanel,
    Rack,
    RackGroup,
    RearPort,
    RearPortTemplate,
)
from nautobot.extras.choices import CustomFieldTypeChoices
from nautobot.extras.models import CustomField, Role, Status
from nautobot.ipam.models import IPAddress, IPAddressToInterface, VLAN
from nautobot.tenancy.models import Tenant


class CableLengthTestCase(TestCase):
    def setUp(self):
        self.location = Location.objects.filter(location_type=LocationType.objects.get(name="Campus")).first()
        self.manufacturer = Manufacturer.objects.create(name="Test Manufacturer 1", slug="test-manufacturer-1")
        self.devicetype = DeviceType.objects.create(
            manufacturer=self.manufacturer,
            model="Test Device Type 1",
            slug="test-device-type-1",
        )
        self.devicerole = Role.objects.get_for_model(Device).first()
        self.device1 = Device.objects.create(
            device_type=self.devicetype,
            role=self.devicerole,
            name="TestDevice1",
            location=self.location,
        )
        self.device2 = Device.objects.create(
            device_type=self.devicetype,
            role=self.devicerole,
            name="TestDevice2",
            location=self.location,
        )
        self.status = Status.objects.get_for_model(Cable).get(name="Connected")

    def test_cable_validated_save(self):
        interface1 = Interface.objects.create(device=self.device1, name="eth0")
        interface2 = Interface.objects.create(device=self.device2, name="eth0")
        cable = Cable(
            termination_a=interface1,
            termination_b=interface2,
            length_unit="ft",
            length=1,
            status=self.status,
        )
        cable.validated_save()
        cable.validated_save()

    def test_cable_full_clean(self):
        interface3 = Interface.objects.create(device=self.device1, name="eth1")
        interface4 = Interface.objects.create(device=self.device2, name="eth1")
        cable = Cable(
            termination_a=interface3,
            termination_b=interface4,
            length_unit="in",
            length=1,
            status=self.status,
        )
        cable.length = 2
        cable.save()
        cable.full_clean()


class InterfaceTemplateCustomFieldTestCase(TestCase):
    def test_instantiate_model(self):
        """
        Check that all _custom_field_data is present and all customfields are filled with the correct default values.
        """
        statuses = Status.objects.get_for_model(Device)
        location = Location.objects.filter(location_type=LocationType.objects.get(name="Campus")).first()
        manufacturer = Manufacturer.objects.create(name="Acme", slug="acme")
        device_role = Role.objects.get_for_model(Device).first()
        custom_fields = [
            CustomField.objects.create(type=CustomFieldTypeChoices.TYPE_TEXT, name="field_1", default="value_1"),
            CustomField.objects.create(type=CustomFieldTypeChoices.TYPE_TEXT, name="field_2", default="value_2"),
            CustomField.objects.create(type=CustomFieldTypeChoices.TYPE_TEXT, name="field_3", default="value_3"),
        ]
        for custom_field in custom_fields:
            custom_field.content_types.set([ContentType.objects.get_for_model(Interface)])
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="FrameForwarder 2048", slug="ff2048")
        interface_template_1 = InterfaceTemplate.objects.create(
            device_type=device_type,
            name="Test_Template_1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            mgmt_only=True,
        )
        interface_template_2 = InterfaceTemplate.objects.create(
            device_type=device_type,
            name="Test_Template_2",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            mgmt_only=True,
        )
        interface_templates = [interface_template_1, interface_template_2]
        device_type.interface_templates.set(interface_templates)
        # instantiate_model() is run when device is created
        device = Device.objects.create(
            device_type=device_type,
            role=device_role,
            status=statuses[0],
            name="Test Device",
            location=location,
        )
        interfaces = device.interfaces.all()
        self.assertEqual(Interface.objects.get(pk=interfaces[0].pk).cf["field_1"], "value_1")
        self.assertEqual(Interface.objects.get(pk=interfaces[0].pk).cf["field_2"], "value_2")
        self.assertEqual(Interface.objects.get(pk=interfaces[0].pk).cf["field_3"], "value_3")
        self.assertEqual(Interface.objects.get(pk=interfaces[1].pk).cf["field_1"], "value_1")
        self.assertEqual(Interface.objects.get(pk=interfaces[1].pk).cf["field_2"], "value_2")
        self.assertEqual(Interface.objects.get(pk=interfaces[1].pk).cf["field_3"], "value_3")


class InterfaceTemplateTestCase(TestCase):
    def test_interface_template_sets_interface_status(self):
        """
        When a device is created with a device type associated with the template,
        assert interface templates sets the interface status.
        """
        statuses = Status.objects.get_for_model(Device)
        location = Location.objects.filter(location_type=LocationType.objects.get(name="Campus")).first()
        manufacturer = Manufacturer.objects.create(name="Acme", slug="acme")
        device_role = Role.objects.get_for_model(Device).first()
        device_type = DeviceType.objects.create(manufacturer=manufacturer, model="FrameForwarder 2048", slug="ff2048")
        InterfaceTemplate.objects.create(
            device_type=device_type,
            name="Test_Template_1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            mgmt_only=True,
        )
        device_1 = Device.objects.create(
            device_type=device_type,
            role=device_role,
            status=statuses[0],
            name="Test Device 1",
            location=location,
        )

        active_status = Status.objects.get(slug="active")
        self.assertEqual(device_1.interfaces.get(name="Test_Template_1").status, active_status)

        # Assert that a different status is picked if active status is not found for interface
        interface_ct = ContentType.objects.get_for_model(Interface)
        active_status.content_types.remove(interface_ct)

        device_2 = Device.objects.create(
            device_type=device_type,
            role=device_role,
            status=statuses[0],
            name="Test Device 2",
            location=location,
        )
        first_status = Status.objects.get_for_model(Interface).first()
        self.assertIsNotNone(device_2.interfaces.get(name="Test_Template_1").status, first_status)


class RackGroupTestCase(TestCase):
    def setUp(self):
        """
        Location A
          - RackGroup A1
            - RackGroup A2
              - Rack 2
            - Rack 1
            - PowerPanel 1
        """
        self.location_type_a = LocationType.objects.get(name="Campus")
        self.location_a = Location.objects.filter(location_type=self.location_type_a).first()
        self.rackgroup_a1 = RackGroup(location=self.location_a, name="RackGroup A1", slug="rackgroup-a1")
        self.rackgroup_a1.save()
        self.rackgroup_a2 = RackGroup(location=self.location_a, parent=self.rackgroup_a1, name="RackGroup A2")
        self.rackgroup_a2.save()

        self.rack1 = Rack.objects.create(location=self.location_a, rack_group=self.rackgroup_a1, name="Rack 1")
        self.rack2 = Rack.objects.create(location=self.location_a, rack_group=self.rackgroup_a2, name="Rack 2")

        self.powerpanel1 = PowerPanel.objects.create(
            location=self.location_a, rack_group=self.rackgroup_a1, name="Power Panel 1"
        )

    def test_rackgroup_location_validation(self):
        """Check that rack group locations are validated correctly."""
        # Group location, if specified, must permit RackGroups
        location_type_c = LocationType.objects.get(name="Elevator")
        location_c = Location.objects.create(name="Location C", location_type=location_type_c)
        child = RackGroup(parent=self.rackgroup_a1, location=location_c, name="Child Group")
        with self.assertRaises(ValidationError) as cm:
            child.validated_save()
        self.assertIn(f'Rack groups may not associate to locations of type "{location_type_c}"', str(cm.exception))

        # Child group location must descend from parent group location
        location_type_d = LocationType.objects.get(name="Room")
        location_type_d.content_types.add(ContentType.objects.get_for_model(RackGroup))
        location_d = Location.objects.create(name="Location D", location_type=location_type_d, parent=location_c)
        child = RackGroup(parent=self.rackgroup_a1, location=location_d, name="Child Group")
        with self.assertRaises(ValidationError) as cm:
            child.validated_save()
        self.assertIn(
            f'Location "Location D" is not descended from parent rack group "RackGroup A1" location "{self.location_a.name}"',
            str(cm.exception),
        )

    def test_change_rackgroup_location_children_permitted(self):
        """
        Check that all child RackGroups, Racks, and PowerPanels get updated when a RackGroup changes Locations.

        In this test, the new Location permits Racks and PowerPanels so the Location should match.
        """
        location_b = Location.objects.create(name="Location B", location_type=self.location_type_a)

        self.rackgroup_a1.location = location_b
        self.rackgroup_a1.save()

        self.assertEqual(RackGroup.objects.get(pk=self.rackgroup_a1.pk).location, location_b)
        self.assertEqual(RackGroup.objects.get(pk=self.rackgroup_a2.pk).location, location_b)
        self.assertEqual(Rack.objects.get(pk=self.rack1.pk).location, location_b)
        self.assertEqual(Rack.objects.get(pk=self.rack2.pk).location, location_b)
        self.assertEqual(PowerPanel.objects.get(pk=self.powerpanel1.pk).location, location_b)

    def test_change_rackgroup_location_children_not_permitted(self):
        """
        Check that all child RackGroups, Racks, and PowerPanels get updated when a RackGroup changes Locations.

        In this test, the new location does not permit Racks and PowerPanels so the Location should be nulled.
        """
        location_type_c = LocationType.objects.create(name="Location Type C", parent=self.location_type_a)
        location_type_c.content_types.add(ContentType.objects.get_for_model(RackGroup))
        location_c = Location.objects.create(name="Location C", location_type=location_type_c, parent=self.location_a)

        self.rackgroup_a1.location = location_c
        with self.assertRaises(ValidationError) as cm:
            self.rackgroup_a1.save()
        self.assertIn(f'Racks may not associate to locations of type "{location_type_c}"', str(cm.exception))
        self.assertEqual(RackGroup.objects.get(pk=self.rackgroup_a2.pk).location, self.location_a)
        self.assertEqual(Rack.objects.get(pk=self.rack1.pk).location, self.location_a)
        self.assertEqual(Rack.objects.get(pk=self.rack2.pk).location, self.location_a)
        self.assertEqual(PowerPanel.objects.get(pk=self.powerpanel1.pk).location, self.location_a)


class RackTestCase(TestCase):
    def setUp(self):

        self.status = Status.objects.get_for_model(Rack).first()
        self.location_type_a = LocationType.objects.create(name="Location Type A")
        self.location_type_a.content_types.add(
            ContentType.objects.get_for_model(RackGroup),
            ContentType.objects.get_for_model(Rack),
            ContentType.objects.get_for_model(Device),
        )

        self.location1 = Location.objects.create(name="Location1", location_type=self.location_type_a)
        self.location2 = Location.objects.create(name="Location2", location_type=self.location_type_a)
        self.group1 = RackGroup.objects.create(name="TestGroup1", slug="test-group-1", location=self.location1)
        self.group2 = RackGroup.objects.create(name="TestGroup2", slug="test-group-2", location=self.location2)
        self.rack = Rack.objects.create(
            name="TestRack1",
            facility_id="A101",
            location=self.location1,
            rack_group=self.group1,
            status=self.status,
            u_height=42,
        )
        self.manufacturer = Manufacturer.objects.create(name="Acme", slug="acme")

        self.device_type = {
            "ff2048": DeviceType.objects.create(
                manufacturer=self.manufacturer,
                model="FrameForwarder 2048",
                slug="ff2048",
            ),
            "cc5000": DeviceType.objects.create(
                manufacturer=self.manufacturer,
                model="CurrentCatapult 5000",
                slug="cc5000",
                u_height=0,
            ),
        }
        self.role = {
            "Server": Role.objects.create(
                name="Server",
                slug="server",
            ),
            "Switch": Role.objects.create(
                name="Switch",
                slug="switch",
            ),
            "Console Server": Role.objects.create(
                name="Console Server",
                slug="console-server",
            ),
            "PDU": Role.objects.create(
                name="PDU",
                slug="pdu",
            ),
        }

    def test_rack_device_outside_height(self):

        rack1 = Rack(
            name="TestRack2",
            facility_id="A102",
            location=self.location1,
            status=self.status,
            u_height=42,
        )
        rack1.save()

        device1 = Device(
            name="TestSwitch1",
            device_type=DeviceType.objects.get(manufacturer__slug="acme", slug="ff2048"),
            role=Role.objects.get(slug="switch"),
            location=self.location1,
            rack=rack1,
            position=43,
            face=DeviceFaceChoices.FACE_FRONT,
        )
        device1.save()

        with self.assertRaises(ValidationError):
            rack1.clean()

    def test_mount_single_device(self):

        device1 = Device(
            name="TestSwitch1",
            device_type=DeviceType.objects.get(manufacturer__slug="acme", slug="ff2048"),
            role=Role.objects.get(slug="switch"),
            location=self.location1,
            rack=self.rack,
            position=10,
            face=DeviceFaceChoices.FACE_REAR,
        )
        device1.save()

        # Validate rack height
        self.assertEqual(list(self.rack.units), list(reversed(range(1, 43))))

        # Validate inventory (front face)
        rack1_inventory_front = self.rack.get_rack_units(face=DeviceFaceChoices.FACE_FRONT)
        self.assertEqual(rack1_inventory_front[-10]["device"], device1)
        del rack1_inventory_front[-10]
        for u in rack1_inventory_front:
            self.assertIsNone(u["device"])

        # Validate inventory (rear face)
        rack1_inventory_rear = self.rack.get_rack_units(face=DeviceFaceChoices.FACE_REAR)
        self.assertEqual(rack1_inventory_rear[-10]["device"], device1)
        del rack1_inventory_rear[-10]
        for u in rack1_inventory_rear:
            self.assertIsNone(u["device"])

    def test_mount_zero_ru(self):
        pdu = Device.objects.create(
            name="TestPDU",
            role=self.role.get("PDU"),
            device_type=self.device_type.get("cc5000"),
            location=self.location1,
            rack=self.rack,
            position=None,
            face="",
        )
        self.assertTrue(pdu)

    def test_change_rack_location_devices_permitted(self):
        """
        Check that changing a Rack's Location also affects child Devices.

        In this test, the new Location also permits Devices.
        """
        # Device1 is explicitly assigned to the same location as the Rack
        device1 = Device.objects.create(
            location=self.location1,
            rack=self.rack,
            device_type=self.device_type["cc5000"],
            role=self.role["Switch"],
        )
        # Device2 is explicitly assigned to the same location as the Rack
        device2 = Device.objects.create(
            location=self.location1,
            rack=self.rack,
            device_type=self.device_type["cc5000"],
            role=self.role["Switch"],
        )

        # Move self.rack to a new location
        location2 = Location.objects.create(name="Location2", location_type=self.location_type_a)
        self.rack.location = location2
        self.rack.save()

        self.assertEqual(Device.objects.get(pk=device1.pk).location, location2)
        self.assertEqual(Device.objects.get(pk=device2.pk).location, location2)

    def test_change_rack_location_devices_not_permitted(self):
        """
        Check that changing a Rack's Location also affects child Devices.

        In this test, the new Location does not permit Devices.
        """
        Device.objects.create(
            location=self.location1,
            rack=self.rack,
            device_type=self.device_type["cc5000"],
            role=self.role["Switch"],
        )

        # Move self.rack to a new location that permits Racks but not Devices
        location_type_b = LocationType.objects.create(name="Location Type B")
        location_type_b.content_types.add(ContentType.objects.get_for_model(Rack))
        location2 = Location.objects.create(name="Location2", location_type=location_type_b)
        self.rack.location = location2
        with self.assertRaises(ValidationError) as cm:
            self.rack.save()
        self.assertIn(f'Devices may not associate to locations of type "{location_type_b}"', str(cm.exception))

    def test_rack_location_validation(self):
        # Rack group location and rack location must relate
        location2 = Location.objects.create(name="Location2", location_type=self.location_type_a)
        rack = Rack(name="Rack", rack_group=self.group1, location=location2, status=self.status)
        with self.assertRaises(ValidationError) as cm:
            rack.validated_save()
        self.assertIn(
            'group "TestGroup1" belongs to a location ("Location1") that does not include location "Location2"',
            str(cm.exception),
        )

        # Location type must permit Racks
        location_type_b = LocationType.objects.create(name="Location Type B")
        locationb = Location.objects.create(name="Location2", location_type=location_type_b)
        rack = Rack(name="Rack", location=locationb, status=self.status)
        with self.assertRaises(ValidationError) as cm:
            rack.validated_save()
        self.assertIn('Racks may not associate to locations of type "Location Type B"', str(cm.exception))


class LocationTypeTestCase(TestCase):
    def test_reserved_names(self):
        """Confirm that certain names are reserved for now."""
        for candidate_name in (
            "RackGroup",
            "rack groups",
        ):
            with self.assertRaises(ValidationError) as cm:
                LocationType(name=candidate_name).clean()
            self.assertIn("This name is reserved", str(cm.exception))

    def test_changing_parent(self):
        """Validate clean logic around changing the parent of a LocationType."""
        parent = LocationType.objects.create(name="Parent LocationType")
        child = LocationType.objects.create(name="Child LocationType")

        # If there are no Locations using it yet, parent can be freely changed
        child.parent = None
        child.validated_save()
        child.parent = parent
        child.validated_save()

        # Once there are Locations using it, parent cannot be changed.
        parent_loc = Location.objects.create(
            name="Parent 1", location_type=parent, status=Status.objects.get_for_model(Location).first()
        )
        child_loc = Location.objects.create(
            name="Child 1", location_type=child, parent=parent_loc, status=Status.objects.get_for_model(Location).last()
        )
        child.parent = None
        with self.assertRaisesMessage(
            ValidationError,
            "This LocationType currently has Locations using it, therefore its parent cannot be changed at this time.",
        ):
            child.validated_save()

        # If the locations are deleted, it again becomes re-parent-able.
        child_loc.delete()
        child.validated_save()


class LocationTestCase(TestCase):
    def setUp(self):
        self.root_type = LocationType.objects.get(name="Campus")
        self.intermediate_type = LocationType.objects.get(name="Building")
        self.leaf_type = LocationType.objects.get(name="Floor")

        self.root_nestable_type = LocationType.objects.get(name="Root")
        self.leaf_nestable_type = LocationType.objects.create(
            name="Pseudo-RackGroup", parent=self.root_nestable_type, nestable=True
        )

        self.status = Status.objects.get(slug="active")

    def test_latitude_or_longitude(self):
        """Test latitude and longitude is parsed to string."""
        active_status = Status.objects.get_for_model(Location).get(name="Active")
        location = Location(
            location_type=self.root_type,
            name="Location A",
            slug="location-a",
            status=active_status,
            longitude=55.1234567896,
            latitude=55.1234567896,
        )
        location.validated_save()

        self.assertEqual(location.longitude, Decimal("55.123457"))
        self.assertEqual(location.latitude, Decimal("55.123457"))

    def test_validate_unique(self):
        """Confirm that the uniqueness constraint on (parent, name) works when parent is None."""
        location_1 = Location(name="Campus 1", location_type=self.root_type, status=self.status)
        location_1.validated_save()

        location_2 = Location(name="Campus 1", location_type=self.root_type, status=self.status)
        with self.assertRaises(ValidationError):
            location_2.validated_save()

    def test_changing_type_forbidden(self):
        """Once created, a location cannot change location_type."""
        location = Location(name="Campus 1", location_type=self.root_type, status=self.status)
        location.validated_save()
        location.location_type = self.root_nestable_type
        with self.assertRaises(ValidationError) as cm:
            location.validated_save()
        self.assertIn("location_type", str(cm.exception))
        self.assertIn("not permitted", str(cm.exception))

    def test_parent_type_must_match(self):
        """A location's parent's location_type must match its location_type's parent."""
        location_1 = Location(name="Building 1", location_type=self.root_type, status=self.status)
        location_1.validated_save()
        location_2 = Location(name="Room 1", location_type=self.leaf_type, parent=location_1, status=self.status)
        with self.assertRaises(ValidationError) as cm:
            location_2.validated_save()
        self.assertIn(
            "A Location of type Floor can only have a Location of type Building as its parent.", str(cm.exception)
        )

    def test_parent_type_nestable_logic(self):
        """A location of a nestable type may have a parent of the same type."""
        # A location using a root-level nestable type can have no parent
        location_1 = Location(name="Region 1", location_type=self.root_nestable_type, status=self.status)
        location_1.validated_save()
        # A location using a root-level nestable type can have no parent
        location_2 = Location(
            name="Region 1-A", location_type=self.root_nestable_type, parent=location_1, status=self.status
        )
        location_2.validated_save()
        # A location using a lower-level nestable type can be parented under the parent location type
        location_3 = Location(
            name="RackGroup 3", location_type=self.leaf_nestable_type, parent=location_2, status=self.status
        )
        location_3.validated_save()
        # A location using a lower-level nestable type can be parented under its own type
        location_4 = Location(
            name="RackGroup 3-B", location_type=self.leaf_nestable_type, parent=location_3, status=self.status
        )
        location_4.validated_save()
        # Can't mix and match location types though
        with self.assertRaises(ValidationError) as cm:
            location_5 = Location(
                name="Region 5", location_type=self.root_nestable_type, parent=location_4, status=self.status
            )
            location_5.validated_save()
        self.assertIn("only have a Location of the same type as its parent", str(cm.exception))
        location_6 = Location(name="Campus 1", location_type=self.root_type, status=self.status)
        location_6.validated_save()
        with self.assertRaises(ValidationError) as cm:
            location_7 = Location(
                name="RackGroup 7",
                location_type=self.leaf_nestable_type,
                parent=location_6,
                status=self.status,
            )
            location_7.validated_save()
        self.assertIn(
            f"only have a Location of the same type or of type {self.root_nestable_type} as its parent",
            str(cm.exception),
        )


class DeviceTestCase(TestCase):
    def setUp(self):

        manufacturer = Manufacturer.objects.create(name="Test Manufacturer 1", slug="test-manufacturer-1")
        self.device_type = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="Test Device Type 1",
            slug="test-device-type-1",
        )
        self.device_role = Role.objects.get_for_model(Device).first()
        self.device_status = Status.objects.get_for_model(Device).get(name="Active")
        self.location_type_1 = LocationType.objects.get(name="Building")
        self.location_type_2 = LocationType.objects.get(name="Floor")
        self.location_type_3 = LocationType.objects.get(name="Campus")
        self.location_type_2.content_types.add(ContentType.objects.get_for_model(Device))
        self.location_type_3.content_types.add(ContentType.objects.get_for_model(Device))
        self.location_1 = Location.objects.create(
            name="Root", status=self.device_status, location_type=self.location_type_1
        )
        self.location_2 = Location.objects.create(
            name="Leaf", status=self.device_status, location_type=self.location_type_2, parent=self.location_1
        )
        self.location_3 = Location.objects.create(
            name="Device Allowed Location",
            status=self.device_status,
            location_type=self.location_type_3,
        )
        self.device_redundancy_group = DeviceRedundancyGroup.objects.first()

        # Create DeviceType components
        ConsolePortTemplate(device_type=self.device_type, name="Console Port 1").save()

        ConsoleServerPortTemplate(device_type=self.device_type, name="Console Server Port 1").save()

        ppt = PowerPortTemplate(
            device_type=self.device_type,
            name="Power Port 1",
            maximum_draw=1000,
            allocated_draw=500,
        )
        ppt.save()

        PowerOutletTemplate(
            device_type=self.device_type,
            name="Power Outlet 1",
            power_port_template=ppt,
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A,
        ).save()

        InterfaceTemplate(
            device_type=self.device_type,
            name="Interface 1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            mgmt_only=True,
        ).save()

        rpt = RearPortTemplate(
            device_type=self.device_type,
            name="Rear Port 1",
            type=PortTypeChoices.TYPE_8P8C,
            positions=8,
        )
        rpt.save()

        FrontPortTemplate(
            device_type=self.device_type,
            name="Front Port 1",
            type=PortTypeChoices.TYPE_8P8C,
            rear_port_template=rpt,
            rear_port_position=2,
        ).save()

        DeviceBayTemplate(device_type=self.device_type, name="Device Bay 1").save()

    def test_device_creation(self):
        """
        Ensure that all Device components are copied automatically from the DeviceType.
        """
        d = Device(
            location=self.location_3,
            device_type=self.device_type,
            role=self.device_role,
            name="Test Device 1",
        )
        d.save()

        ConsolePort.objects.get(device=d, name="Console Port 1")

        ConsoleServerPort.objects.get(device=d, name="Console Server Port 1")

        pp = PowerPort.objects.get(device=d, name="Power Port 1", maximum_draw=1000, allocated_draw=500)

        PowerOutlet.objects.get(
            device=d,
            name="Power Outlet 1",
            power_port=pp,
            feed_leg=PowerOutletFeedLegChoices.FEED_LEG_A,
        )

        Interface.objects.get(
            device=d,
            name="Interface 1",
            type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            mgmt_only=True,
        )

        rp = RearPort.objects.get(device=d, name="Rear Port 1", type=PortTypeChoices.TYPE_8P8C, positions=8)

        FrontPort.objects.get(
            device=d,
            name="Front Port 1",
            type=PortTypeChoices.TYPE_8P8C,
            rear_port=rp,
            rear_port_position=2,
        )

        DeviceBay.objects.get(device=d, name="Device Bay 1")

    def test_multiple_unnamed_devices(self):

        device1 = Device(
            location=self.location_3,
            device_type=self.device_type,
            role=self.device_role,
            status=self.device_status,
            name="",
        )
        device1.save()

        device2 = Device(
            location=device1.location,
            device_type=device1.device_type,
            role=device1.role,
            status=self.device_status,
            name="",
        )
        device2.full_clean()
        device2.save()

        self.assertEqual(Device.objects.filter(name="").count(), 2)

    def test_device_duplicate_names(self):

        device1 = Device(
            location=self.location_3,
            device_type=self.device_type,
            role=self.device_role,
            status=self.device_status,
            name="Test Device 1",
        )
        device1.save()

        device2 = Device(
            location=device1.location,
            device_type=device1.device_type,
            role=device1.role,
            status=self.device_status,
            name=device1.name,
        )

        # Two devices assigned to the same Location and no Tenant should fail validation
        with self.assertRaises(ValidationError):
            device2.full_clean()

        tenant = Tenant.objects.create(name="Test Tenant 1", slug="test-tenant-1")
        device1.tenant = tenant
        device1.save()
        device2.tenant = tenant

        # Two devices assigned to the same Location and the same Tenant should fail validation
        with self.assertRaises(ValidationError):
            device2.full_clean()

        device2.tenant = None

        # Two devices assigned to the same Location and different Tenants should pass validation
        device2.full_clean()
        device2.save()

    def test_device_location_content_type_not_allowed(self):
        device = Device(
            name="Device 3",
            device_type=self.device_type,
            role=self.device_role,
            status=self.device_status,
            location=self.location_1,
        )
        with self.assertRaises(ValidationError) as cm:
            device.validated_save()
        self.assertIn(
            f'Devices may not associate to locations of type "{self.location_type_1.name}"', str(cm.exception)
        )

    def test_device_redundancy_group_validation(self):
        d1 = Device(
            name="Test Device 1",
            device_type=self.device_type,
            role=self.device_role,
            status=self.device_status,
            location=self.location_3,
        )
        d1.validated_save()

        d2 = Device(
            name="Test Device 2",
            device_type=self.device_type,
            role=self.device_role,
            status=self.device_status,
            location=self.location_3,
        )
        d2.validated_save()

        # Validate we can set a redundancy group without any priority set
        d1.device_redundancy_group = self.device_redundancy_group
        d1.validated_save()

        # Validate two devices can be a part of the same redundancy group without any priority set
        d2.device_redundancy_group = self.device_redundancy_group
        d2.validated_save()

        # Validate we can assign a priority to at least one device in the group
        d1.device_redundancy_group_priority = 1
        d1.validated_save()

        # Validate both devices in the same group can have the same priority
        d2.device_redundancy_group_priority = 1
        d2.validated_save()

        # Validate devices in the same group can have different priority
        d2.device_redundancy_group_priority = 2
        d2.validated_save()

        # Validate devices cannot have an assigned priority without an assigned group
        d1.device_redundancy_group = None
        with self.assertRaisesMessage(
            ValidationError, "Must assign a redundancy group when defining a redundancy group priority."
        ):
            d1.validated_save()


class CableTestCase(TestCase):
    def setUp(self):

        location = Location.objects.first()
        manufacturer = Manufacturer.objects.create(name="Test Manufacturer 1", slug="test-manufacturer-1")
        devicetype = DeviceType.objects.create(
            manufacturer=manufacturer,
            model="Test Device Type 1",
            slug="test-device-type-1",
        )
        devicerole = Role.objects.get_for_model(Device).first()
        self.device1 = Device.objects.create(
            device_type=devicetype,
            role=devicerole,
            name="TestDevice1",
            location=location,
        )
        self.device2 = Device.objects.create(
            device_type=devicetype,
            role=devicerole,
            name="TestDevice2",
            location=location,
        )
        self.interface1 = Interface.objects.create(device=self.device1, name="eth0")
        self.interface2 = Interface.objects.create(device=self.device2, name="eth0")
        self.interface3 = Interface.objects.create(device=self.device2, name="eth1")
        self.status = Status.objects.get_for_model(Cable).get(name="Connected")
        self.cable = Cable(
            termination_a=self.interface1,
            termination_b=self.interface2,
            status=self.status,
        )
        self.cable.save()

        self.power_port1 = PowerPort.objects.create(device=self.device2, name="psu1")
        self.patch_panel = Device.objects.create(
            device_type=devicetype,
            role=devicerole,
            name="TestPatchPanel",
            location=location,
        )
        self.rear_port1 = RearPort.objects.create(device=self.patch_panel, name="RP1", type="8p8c")
        self.front_port1 = FrontPort.objects.create(
            device=self.patch_panel,
            name="FP1",
            type="8p8c",
            rear_port=self.rear_port1,
            rear_port_position=1,
        )
        self.rear_port2 = RearPort.objects.create(device=self.patch_panel, name="RP2", type="8p8c", positions=2)
        self.front_port2 = FrontPort.objects.create(
            device=self.patch_panel,
            name="FP2",
            type="8p8c",
            rear_port=self.rear_port2,
            rear_port_position=1,
        )
        self.rear_port3 = RearPort.objects.create(device=self.patch_panel, name="RP3", type="8p8c", positions=3)
        self.front_port3 = FrontPort.objects.create(
            device=self.patch_panel,
            name="FP3",
            type="8p8c",
            rear_port=self.rear_port3,
            rear_port_position=1,
        )
        self.rear_port4 = RearPort.objects.create(device=self.patch_panel, name="RP4", type="8p8c", positions=3)
        self.front_port4 = FrontPort.objects.create(
            device=self.patch_panel,
            name="FP4",
            type="8p8c",
            rear_port=self.rear_port4,
            rear_port_position=1,
        )
        self.provider = Provider.objects.create(name="Provider 1", slug="provider-1")
        provider_network = ProviderNetwork.objects.create(name="Provider Network 1", provider=self.provider)
        self.circuittype = CircuitType.objects.create(name="Circuit Type 1", slug="circuit-type-1")
        self.circuit1 = Circuit.objects.create(provider=self.provider, circuit_type=self.circuittype, cid="1")
        self.circuit2 = Circuit.objects.create(provider=self.provider, circuit_type=self.circuittype, cid="2")
        self.circuittermination1 = CircuitTermination.objects.create(
            circuit=self.circuit1, location=location, term_side="A"
        )
        self.circuittermination2 = CircuitTermination.objects.create(
            circuit=self.circuit1, location=location, term_side="Z"
        )
        self.circuittermination3 = CircuitTermination.objects.create(
            circuit=self.circuit2, provider_network=provider_network, term_side="Z"
        )

    def test_cable_creation(self):
        """
        When a new Cable is created, it must be cached on either termination point.
        """
        interface1 = Interface.objects.get(pk=self.interface1.pk)
        interface2 = Interface.objects.get(pk=self.interface2.pk)
        self.assertEqual(self.cable.termination_a, interface1)
        self.assertEqual(interface1._cable_peer, interface2)
        self.assertEqual(self.cable.termination_b, interface2)
        self.assertEqual(interface2._cable_peer, interface1)

    def test_cable_deletion(self):
        """
        When a Cable is deleted, the `cable` field on its termination points must be nullified. The str() method
        should still return the PK of the string even after being nullified.
        """
        self.cable.delete()
        self.assertIsNone(self.cable.pk)
        self.assertNotEqual(str(self.cable), "#None")
        interface1 = Interface.objects.get(pk=self.interface1.pk)
        self.assertIsNone(interface1.cable)
        self.assertIsNone(interface1._cable_peer)
        interface2 = Interface.objects.get(pk=self.interface2.pk)
        self.assertIsNone(interface2.cable)
        self.assertIsNone(interface2._cable_peer)

    def test_cabletermination_deletion(self):
        """
        When a CableTermination object is deleted, its attached Cable (if any) must also be deleted.
        """
        self.interface1.delete()
        cable = Cable.objects.filter(pk=self.cable.pk).first()
        self.assertIsNone(cable)

    def test_cable_validates_compatible_types(self):
        """
        The clean method should have a check to ensure only compatible port types can be connected by a cable
        """
        # An interface cannot be connected to a power port
        cable = Cable(termination_a=self.interface1, termination_b=self.power_port1)
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_cannot_have_the_same_terminination_on_both_ends(self):
        """
        A cable cannot be made with the same A and B side terminations
        """
        cable = Cable(termination_a=self.interface1, termination_b=self.interface1)
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_front_port_cannot_connect_to_corresponding_rear_port(self):
        """
        A cable cannot connect a front port to its corresponding rear port
        """
        cable = Cable(termination_a=self.front_port1, termination_b=self.rear_port1)
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_cannot_terminate_to_an_existing_connection(self):
        """
        Either side of a cable cannot be terminated when that side already has a connection
        """
        # Try to create a cable with the same interface terminations
        cable = Cable(termination_a=self.interface2, termination_b=self.interface1)
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_cannot_terminate_to_a_provider_network_circuittermination(self):
        """
        Neither side of a cable can be terminated to a CircuitTermination which is attached to a Provider Network
        """
        cable = Cable(termination_a=self.interface3, termination_b=self.circuittermination3)
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_rearport_connections(self):
        """
        Test various combinations of RearPort connections.
        """
        # Connecting a single-position RearPort to a multi-position RearPort is ok
        Cable(
            termination_a=self.rear_port1,
            termination_b=self.rear_port2,
            status=self.status,
        ).full_clean()

        # Connecting a single-position RearPort to an Interface is ok
        Cable(
            termination_a=self.rear_port1,
            termination_b=self.interface3,
            status=self.status,
        ).full_clean()

        # Connecting a single-position RearPort to a CircuitTermination is ok
        Cable(
            termination_a=self.rear_port1,
            termination_b=self.circuittermination1,
            status=self.status,
        ).full_clean()

        # Connecting a multi-position RearPort to another RearPort with the same number of positions is ok
        Cable(
            termination_a=self.rear_port3,
            termination_b=self.rear_port4,
            status=self.status,
        ).full_clean()

        # Connecting a multi-position RearPort to an Interface is ok
        Cable(
            termination_a=self.rear_port2,
            termination_b=self.interface3,
            status=self.status,
        ).full_clean()

        # Connecting a multi-position RearPort to a CircuitTermination is ok
        Cable(
            termination_a=self.rear_port2,
            termination_b=self.circuittermination1,
            status=self.status,
        ).full_clean()

        # Connecting a two-position RearPort to a three-position RearPort is NOT ok
        with self.assertRaises(
            ValidationError,
            msg="Connecting a 2-position RearPort to a 3-position RearPort should fail",
        ):
            Cable(termination_a=self.rear_port2, termination_b=self.rear_port3).full_clean()

    def test_cable_cannot_terminate_to_a_virtual_interface(self):
        """
        A cable cannot terminate to a virtual interface
        """
        virtual_interface = Interface(device=self.device1, name="V1", type=InterfaceTypeChoices.TYPE_VIRTUAL)
        cable = Cable(termination_a=self.interface2, termination_b=virtual_interface)
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_cable_cannot_terminate_to_a_wireless_interface(self):
        """
        A cable cannot terminate to a wireless interface
        """
        wireless_interface = Interface(device=self.device1, name="W1", type=InterfaceTypeChoices.TYPE_80211A)
        cable = Cable(termination_a=self.interface2, termination_b=wireless_interface)
        with self.assertRaises(ValidationError):
            cable.clean()

    def test_create_cable_with_missing_status_connected(self):
        """Test for https://github.com/nautobot/nautobot/issues/2081"""
        # Delete all cables because some cables has connected status.
        Cable.objects.all().delete()
        Status.objects.get(slug=CableStatusChoices.STATUS_CONNECTED).delete()
        device = Device.objects.first()

        interfaces = (
            Interface.objects.create(
                device=device,
                name="eth-0",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
            Interface.objects.create(
                device=device,
                name="eth-1",
                type=InterfaceTypeChoices.TYPE_1GE_FIXED,
            ),
        )

        cable = Cable.objects.create(
            termination_a=interfaces[0],
            termination_b=interfaces[1],
            type=CableTypeChoices.TYPE_CAT6,
        )

        self.assertTrue(Cable.objects.filter(id=cable.pk).exists())


class PowerPanelTestCase(TestCase):
    def test_power_panel_validation(self):
        active = Status.objects.get(name="Active")
        location_type_1 = LocationType.objects.create(name="Location Type 1")
        location_1 = Location.objects.create(name="Location 1", location_type=location_type_1, status=active)
        power_panel = PowerPanel(name="Power Panel 1", location=location_1)
        with self.assertRaises(ValidationError) as cm:
            power_panel.validated_save()
        self.assertIn(f'Power panels may not associate to locations of type "{location_type_1}"', str(cm.exception))

        location_type_1.content_types.add(ContentType.objects.get_for_model(PowerPanel))
        rack_group = RackGroup.objects.create(name="Rack Group 1", location=location_1)
        power_panel.rack_group = rack_group
        location_2 = Location.objects.create(name="Location 2", location_type=location_type_1, status=active)
        rack_group.location = location_2
        rack_group.save()
        with self.assertRaises(ValidationError) as cm:
            power_panel.validated_save()
        self.assertIn(
            f'Rack group "Rack Group 1" belongs to a location ("{location_2.name}") that does not contain "{location_1.name}"',
            str(cm.exception),
        )


class InterfaceTestCase(TestCase):
    def setUp(self):
        manufacturer = Manufacturer.objects.create(name="Manufacturer 1", slug="manufacturer-1")
        devicetype = DeviceType.objects.create(manufacturer=manufacturer, model="Device Type 1", slug="device-type-1")
        devicerole = Role.objects.get_for_model(Device).first()
        location = Location.objects.filter(location_type=LocationType.objects.get(name="Campus")).first()
        self.vlan = VLAN.objects.create(name="VLAN 1", vid=100, location=location)
        status = Status.objects.get_for_model(Device)[0]
        self.device = Device.objects.create(
            name="Device 1",
            device_type=devicetype,
            role=devicerole,
            location=location,
            status=status,
        )
        self.other_location_vlan = VLAN.objects.create(
            name="Other Location VLAN",
            vid=100,
            location=Location.objects.create(
                name="Other Location", location_type=LocationType.objects.get(name="Campus")
            ),
        )

    def test_tagged_vlan_raise_error_if_mode_not_set_to_tagged(self):
        interface = Interface.objects.create(
            name="Int1",
            type=InterfaceTypeChoices.TYPE_VIRTUAL,
            device=self.device,
        )
        with self.assertRaises(ValidationError) as err:
            interface.tagged_vlans.add(self.vlan)
        self.assertEqual(
            err.exception.message_dict["tagged_vlans"][0], "Mode must be set to tagged when specifying tagged_vlans"
        )

    def test_error_raised_when_adding_tagged_vlan_with_different_location_from_interface_parent_location(self):
        with self.assertRaises(ValidationError) as err:
            interface = Interface.objects.create(
                name="Test Interface",
                mode=InterfaceModeChoices.MODE_TAGGED,
                device=self.device,
            )
            interface.tagged_vlans.add(self.other_location_vlan)
        self.assertEqual(
            err.exception.message_dict["tagged_vlans"][0],
            f"Tagged VLAN with names {[self.other_location_vlan.name]} must all belong to the "
            f"same location as the interface's parent device, or it must be global.",
        )

    def test_add_ip_addresses(self):
        """Test the `add_ip_addresses` helper method on `Interface`"""
        interface = Interface.objects.create(
            name="Int1",
            type=InterfaceTypeChoices.TYPE_VIRTUAL,
            device=self.device,
        )
        ips = list(IPAddress.objects.all()[:10])

        # baseline (no interface to ip address relationships exists)
        self.assertFalse(IPAddressToInterface.objects.filter(interface=interface).exists())

        # add single instance
        count = interface.add_ip_addresses(ips[-1])
        self.assertEqual(count, 1)
        self.assertEqual(IPAddressToInterface.objects.filter(ip_address=ips[-1], interface=interface).count(), 1)

        # add multiple instances
        count = interface.add_ip_addresses(ips[:5])
        self.assertEqual(count, 5)
        self.assertEqual(IPAddressToInterface.objects.filter(interface=interface).count(), 6)
        for ip in ips[:5]:
            self.assertEqual(IPAddressToInterface.objects.filter(ip_address=ip, interface=interface).count(), 1)

    def test_remove_ip_addresses(self):
        """Test the `remove_ip_addresses` helper method on `Interface`"""
        interface = Interface.objects.create(
            name="Int1",
            type=InterfaceTypeChoices.TYPE_VIRTUAL,
            device=self.device,
        )
        ips = list(IPAddress.objects.all()[:10])

        # baseline (no interface to ip address relationships exists)
        self.assertFalse(IPAddressToInterface.objects.filter(interface=interface).exists())

        interface.add_ip_addresses(ips)
        self.assertEqual(IPAddressToInterface.objects.filter(interface=interface).count(), 10)

        # remove single instance
        count = interface.remove_ip_addresses(ips[-1])
        self.assertEqual(count, 1)
        self.assertEqual(IPAddressToInterface.objects.filter(interface=interface).count(), 9)

        # remove multiple instances
        count = interface.remove_ip_addresses(ips[:5])
        self.assertEqual(count, 5)
        self.assertEqual(IPAddressToInterface.objects.filter(interface=interface).count(), 4)

        count = interface.remove_ip_addresses(ips)
        self.assertEqual(count, 4)
        self.assertEqual(IPAddressToInterface.objects.filter(interface=interface).count(), 0)
