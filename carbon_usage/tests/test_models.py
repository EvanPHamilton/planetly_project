from django.test import TestCase
from ..models import UsageType, Usage
from django.contrib.auth.models import User
from django.utils import timezone


class UsageTypeTest(TestCase):
    """ UsageType tests"""

    def setUp(self):
        UsageType.objects.create(
            name="driving", unit="kilometers")
        UsageType.objects.create(
            name="sailing", unit="nautical miles")

    def test_usage_type(self):
        # Check that we can get objects by name or unit
        driving = UsageType.objects.get(name='driving')
        sailing = UsageType.objects.get(unit='nautical miles')
        self.assertEqual(
            driving.unit, "kilometers")
        self.assertEqual(
            sailing.name, "sailing")
        # Check that we cannot get what is not there
        try:
            flying = UsageType.objects.get(name='flying')
        except UsageType.DoesNotExist:
            pass


class UsageTest(TestCase):
    """ Usage tests"""

    def setUp(self):
        # Create a user and usagetype,
        # which we will associate with our usage
        User.objects.create(username="planetly")
        UsageType.objects.create(name='driving')
        planetly = User.objects.get(username='planetly')
        driving = UsageType.objects.get(name='driving')

        Usage.objects.create(user=planetly, usage_type=driving,
                             usage_at=timezone.now())

    def test_usage(self):
        # Check that usages store expected information
        first_usage = Usage.objects.get(id=1)
        self.assertEqual(
            first_usage.user.username, "planetly")
        self.assertEqual(
            first_usage.usage_type.name, "driving")
        self.assertLess(
            first_usage.usage_at, timezone.now())
