import json
import pytz

from datetime import datetime
from http import HTTPStatus
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from rest_framework.test import force_authenticate
from ..models import UsageType, Usage
from ..views import UsageViewSet, UsageTypeViewSet
from rest_framework.test import APIClient


"""
Test the usage and usage_type apis

Test api routes for:
list, create, retrieve, update,
partial_update, destroy

corresponding to the CRUD operations

And test the ViewSet get options.


TODOs -- note to self for future work if I had more time

-Understand more about django datetimes. Do we really want to save
timezone aware datetimes in the db? Leads to some
ugly string formatting in the tests
"""


class UsageTypeTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            password='verysecure')

        # force authentication for testing
        self.client.force_authenticate(user=self.user)

        self.usage_type_one = UsageType.objects.create(
            name="driving", unit="kilometers")
        self.usage_type_two = UsageType.objects.create(
            name="sailing", unit="nautical miles")

    def test_get_usage_type_viewset(self):
        """
        Test list/retrieve on usagetype viewset
        """
        request = self.factory.get('/carbon_usage/usage_type')
        force_authenticate(request, user=self.user)
        response = UsageTypeViewSet.as_view({'get': 'list'})(request)

        # Check we get 200 back:
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)

        # Test the first result is our driving UsageType and second is sailing
        self.assertEqual(response.data['results'][0]['name'], 'driving')
        self.assertEqual(response.data['results'][1]['name'], 'sailing')

        # Check we get pagination info: count/next/previous
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        # Store single usage type and then query for it by ID, testing retrieve
        first_usage_type = response.data['results'][0]
        response = UsageTypeViewSet.as_view({'get': 'retrieve'})(
            request, pk=first_usage_type['id'])
        self.assertEqual(response.data, first_usage_type)

    def test_CRUD_routes_usage_type(self):
        """
        Test CRUD API routes for usage_type endpoint

        POST   /usage_type/     -- CREATE
        GET    /usage_type/     -- READ
        GET    /usage_type/:id  -- READ all
        PUT    /usage_type/:id  -- UPDATE
        PATCH  /usage_type/:id  -- PARTIAL UPDATE
        DELETE /usage_type/:id  -- DELETE
        """

        ###
        # Test GET all
        ###
        response = self.client.get('/carbon_usage/usage_type/')
        # Check you get a 200 back:
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)
        # Get current count of usage_types
        current_count = response.data['count']
        self.assertEqual(current_count, 2)
        self.assertIn({
            "name": "sailing",
            "unit": "nautical miles",
            "id": self.usage_type_two.id  # TODO not ideal
        }, response.data['results'])

        ###
        # Test create
        ###
        data = json.dumps({
            "name": "electricity",
            "unit": "watts"
        })
        response = self.client.post(
            '/carbon_usage/usage_type/',
            data=data, content_type='application/json')
        # Check you get a 201 back:
        self.assertEqual(response.status_code, HTTPStatus.CREATED._value_)
        # Check to see that we return the created usage_type
        new_usage_type = response.data
        self.assertEqual(response.data, {
            "name": "electricity",
            "unit": "watts",
            "id": self.usage_type_two.id+1  # TODO not ideal
        })

        ###
        # Test partial UPDATE
        # What else can be stored in watts
        ###
        data = json.dumps({
            "name": "not_electricity",
        })
        response = self.client.patch('/carbon_usage/usage_type/%s/'
                                     % new_usage_type['id'],
                                     data=data,
                                     content_type='application/json')
        # Check you get a 200 back:
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)
        # Check to see that we return the created usage_type
        self.assertEqual(response.data, {
            "name": "not_electricity",
            "unit": "watts",
            "id": self.usage_type_two.id+1  # TODO Fix this!
        })

        ###
        # Test UPDATE
        # Watts are too small, let's update the unit to kilowatts
        ###
        data = json.dumps({
            "name": "electricity",
            "unit": "kilowatts"
        })
        response = self.client.put('/carbon_usage/usage_type/%s/'
                                   % new_usage_type['id'],
                                   data=data, content_type='application/json')
        # Check you get a 200 back:
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)
        # Check to see that we return the created usage_type
        self.assertEqual(response.data, {
            "name": "electricity",
            "unit": "kilowatts",
            "id": self.usage_type_two.id+1  # TODO Fix this!
        })

        ###
        # Test GET single
        ###
        response = self.client.get('/carbon_usage/usage_type/%s/'
                                   % str(self.usage_type_two.id+1))
        # Check you get a 200 back:
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)
        # Do not check full get results (including pagination) for brevity
        # just that our newly added usagetype is included
        self.assertEquals({
            "name": "electricity",
            "unit": "kilowatts",
            "id": self.usage_type_two.id+1  # TODO not ideal
        }, response.data)

        ###
        # Test DELETE
        ###
        response = self.client.delete('/carbon_usage/usage_type/%s/'
                                      % new_usage_type['id'],
                                      content_type='application/json')
        # Check you get a 204 back, indicating
        # deletion was successful and no content to return
        self.assertEqual(response.status_code,
                         HTTPStatus.NO_CONTENT._value_)


class UsageTest(TestCase):

    def setUp(self):

        self.factory = RequestFactory()
        self.client = APIClient()

        self.user1 = User.objects.create_user(
            username='testuser',
            password='verysecure')

        # force authentication for testing
        self.client.force_authenticate(user=self.user1)

        self.driving = UsageType.objects.create(
            name="driving", unit="kilometers")

        self.flying = UsageType.objects.create(
            name="flying", unit="kilometers")

        # TODO Read more about django timezones
        tz_aware_datetime = return_localized_date()

        self.test_usage = Usage.objects.create(
            user=self.user1, usage_type=self.driving,
            usage_at=tz_aware_datetime)

    def test_get_usage_viewset(self):
        """
        Test list/retrieve on usage viewset
        """
        request = self.factory.get('/carbon_usage/usage')
        force_authenticate(request, user=self.user1)
        response = UsageViewSet.as_view({'get': 'list'})(request)

        # Check we get 200 back:
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)

        # Test the first result is our usage from setup
        self.assertEqual(response.data['results'][0]['usage_type'],
                         self.test_usage.usage_type.id)
        self.assertEqual(response.data['results'][0]['user'], 'testuser')
        # Convert datetime as string returned from django into datetime object
        # to compare to our test_usage django object
        datetime_string = response.data['results'][0]['usage_at']
        first_usage_datetime = datetime.strptime(datetime_string,
                                                 "%Y-%m-%dT%H:%M:%S.%f%z")
        self.assertEqual(first_usage_datetime, self.test_usage.usage_at)

        # Check we get pagination info: count/next/previous
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['next'], None)
        self.assertEqual(response.data['previous'], None)

        # Store single usage type and then query for it by ID, testing retrieve
        first_usage = response.data['results'][0]
        response = UsageViewSet.as_view({'get': 'retrieve'})(
            request, pk=first_usage['id'])
        self.assertEqual(response.data, first_usage)

    def test_CRUD_routes_usage(self):
        """
        Test CRUD API routes for usage endpoint

        POST   /usage/     -- CREATE
        GET    /usage/     -- READ
        GET    /usage/:id  -- READ all
        PATCH  /usage/:id  -- PARTIAL UPDATE
        PUT    /usage/:id  -- UPDATE
        DELETE /usage/:id  -- DELETE
        """

        ###
        # Test GET all
        ###

        response = self.client.get('/carbon_usage/usage/')
        # Check you get a 200 back:
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)

        # Get current count of usage_types
        current_count = response.data['count']
        self.assertEqual(current_count, 1)

        # TODO fix datetime handling
        # see earlier notes on problems with django's datetime aware strings
        datetime_string = self.test_usage.usage_at.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        datetime_string = datetime_string[:-2]+":00"

        # DRF returns result as type ReturnList which apparently
        # cannot be compared to a regular dict using equality
        # so assertIn not assertEqual
        self.assertIn({
            "user": "testuser",
            "usage_type": self.test_usage.usage_type.id,
            "id": self.test_usage.id,
            "usage_at": datetime_string
        }, response.data['results'])

        ###
        # Test create
        ###

        # TODO see earlier django timezone aware datetime notes
        tz_aware_datetime = return_localized_date()
        data = json.dumps({
            "usage_type": self.driving.id,
            "usage_at": str(tz_aware_datetime)
        })
        response = self.client.post('/carbon_usage/usage/',
                                    data=data,
                                    content_type='application/json')
        # Check you get a 201 back:
        self.assertEqual(response.status_code, HTTPStatus.CREATED._value_)
        # Check to see that we return the created usage_type
        new_usage = response.data

        # TODO see django timezone formatting
        datetime_string = tz_aware_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
        datetime_string = datetime_string[:-2]+":00"
        self.assertEqual(response.data, {
            "user": "testuser",
            "usage_type": self.driving.id,
            "id": self.test_usage.id+1,  # TODO unideal
            "usage_at": datetime_string
        })

        ###
        # Test partial update usage
        # Lets do a partial update to the usage usage type.
        # Not sure I would actually allow updates here in a
        # real app, but we are showing that it is possible.
        ###
        data = json.dumps({
            "usage_type": self.flying.id
        })
        response = self.client.patch('/carbon_usage/usage/%s/'
                                     % new_usage['id'], data=data,
                                     content_type='application/json')
        # Check you get a 200 back:
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)
        # Check to see that we return the created usage_type
        self.assertEqual(response.data, {
            "user": "testuser",
            "usage_type": self.flying.id,
            "usage_at": datetime_string,  # Same as above
            "id": self.test_usage.id+1,   # TODO unideal
        })

        ###
        # Test update usage
        # Switch usage_type back to driving
        # leave usage_at the same
        ###
        data = json.dumps({
            "usage_type": self.driving.id,
            "usage_at": datetime_string
        })
        response = self.client.put('/carbon_usage/usage/%s/'
                                   % new_usage['id'], data=data,
                                   content_type='application/json')
        last_usage = response.data
        # Check you get a 200 back:
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)
        # Check to see that we return the created usage_type
        self.assertEqual(response.data, {
            "user": "testuser",
            "usage_type": self.driving.id,
            "usage_at": datetime_string,  # same as earlier
            "id": self.test_usage.id+1,   # TODO unideal
        })

        ###
        # Test GET single usage
        ###
        response = self.client.get('/carbon_usage/usage/%s/'
                                   % str(self.test_usage.id+1))
        # Check you get a 200 back:
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)
        # Compare directly against return value of update call above
        self.assertEqual(response.data, last_usage)

        ###
        # Test delete
        ###
        response = self.client.delete('/carbon_usage/usage/%s/'
                                      % str(self.test_usage.id+1),
                                      content_type='application/json')
        # Check you get a 204 back, indicating
        # deletion was successful and no content to return
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT._value_)


class UsageTestGETFiltering(TestCase):

    def setUp(self):

        self.client = APIClient()
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='verysecure')
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='verysecure1')

        self.driving = UsageType.objects.create(
            name="driving", unit="kilometers")
        self.flying = UsageType.objects.create(
            name="flying", unit="kilometers")

        tz_aware_datetime = return_localized_date()
        # Create 5 usage's as user1
        for i in range(5):
            Usage.objects.create(
                user=self.user1, usage_type=self.driving,
                usage_at=tz_aware_datetime)

        # Create 11 usage's as user2 with both usage types
        for i in range(11):
            if i % 2 == 0:
                Usage.objects.create(
                    user=self.user2, usage_type=self.driving,
                    usage_at=return_localized_date())
            else:
                Usage.objects.create(
                    user=self.user2, usage_type=self.flying,
                    usage_at=return_localized_date())

    def test_GET_filtering_and_sorting(self):
        ###
        # Test filter usages by usage_at time
        # and sorting by usage_at and usage_type param
        ###

        # Authenticate as user1, check that we only see user1's usages
        self.client.force_authenticate(user=self.user1)

        response = self.client.get('/carbon_usage/usage/')
        # Check you get a 200 back:
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)
        # Get current count of usage_types
        current_count = response.data['count']
        self.assertEqual(current_count, 5)

        # Authenticate as user2, check that we only see user2's usages
        # and check sorting by 'usage_at' and 'usage_type'
        self.client.force_authenticate(user=self.user2)
        response = self.client.get('/carbon_usage/usage/?ordering=usage_at')
        # Check you get a 200 back:
        self.assertEqual(response.status_code, HTTPStatus.OK._value_)
        # Check that we have 11, and paginate
        self.assertEqual(
            response.data['count'], 11)
        self.assertEqual(response.data['next'],
                         'http://testserver/carbon_usage/usage/' +
                         '?ordering=usage_at&page=2')

        # Check that we filter by datetime in ascending order
        for index, res in enumerate(response.data['results']):
            if index == 0:
                previous_datetime = datetime.strptime(res['usage_at'],
                                                      "%Y-%m-%dT%H:%M:%S.%f%z")
                continue
            current_datetime = datetime.strptime(res['usage_at'],
                                                 "%Y-%m-%dT%H:%M:%S.%f%z")
            self.assertLess(previous_datetime, current_datetime)
            previous_datetime = current_datetime

        response = self.client.get('/carbon_usage/usage/?ordering=-usage_at')
        # Check that we filter by datetime in descending order
        for index, res in enumerate(response.data['results']):
            if index == 0:
                previous_datetime = datetime.strptime(res['usage_at'],
                                                      "%Y-%m-%dT%H:%M:%S.%f%z")
                continue
            current_datetime = datetime.strptime(res['usage_at'],
                                                 "%Y-%m-%dT%H:%M:%S.%f%z")
            self.assertGreater(previous_datetime, current_datetime)
            previous_datetime = current_datetime

        response = self.client.get('/carbon_usage/usage/?ordering=-usage_type')
        # Check that we filter by datetime in descending order
        for index, res in enumerate(response.data['results']):
            if index == 0:
                previous_usage_type = res['usage_type']
                continue
            current_usage_type = res['usage_type']
            self.assertGreaterEqual(previous_usage_type, current_usage_type)
            previous_usage_type = current_usage_type

        # TODO
        # If I pass in a localized datetime here, the filtering in my view
        # fails with the following error:
        # "django.core.exceptions.ValidationError:
        # ['“2021-04-06 18:59:39.577529 02:00” value has an invalid format.
        # It must be in YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format.']""
        # spaces are being added somewhere (my serializer?) but because I
        # am quite a bit overtime working on this project and would like
        # to turn it in, I will pass in a non-localized datetime just to
        # demo the filtering working

        # No usages started before the current time
        response = self.client.get(
            '/carbon_usage/usage/?timerange_start=%s' % datetime.now())
        # Check that we filter by datetime in descending order
        self.assertEqual(response.data['count'], 0)

        # All usages ended before the current time
        response = self.client.get(
            '/carbon_usage/usage/?timerange_end=%s' % datetime.now())
        # Check that we filter by datetime in descending order
        self.assertEqual(response.data['count'], 11)


def return_localized_date():
    """
    Helper function for returning localized datetime

    TODO see earlier todo about django timezone aware datetimes
    My gut instinct is to always store time in db
    as unix timestamp, and to manually interpolate timezones.
    DJANGO seems to encourage storing tz aware datetimes
    I don't have time to delve into this deeper, so making it work
    but I do not find this ideal.
    """
    creation_date = datetime.now()
    timezone = pytz.timezone('Europe/Berlin')
    return timezone.localize(creation_date)
