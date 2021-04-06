import requests
from datetime import datetime, timezone
import pytz

"""
Run this file to test all the api routes

Endpoints 		HTTP Method CRUD Method Result
usage_type 		GET 		READ 		Get all usage types
usage_type/:id 	GET 		READ		Get a single usage type
usage_type  	POST 		CREATE 		Add a single usage type
usage_type/:id 	PUT 		UPDATE 		Update a single usage type
usage_type/:id 	DELETE 		DELETE 		Delete a single usage type

usage 			GET 		READ 		Get all usages (for a given user)
usage/:id 		GET 		READ		Get a single usage
usage  			POST 		CREATE 		Add a single usage
usage/:id 		PUT 		UPDATE 		Update a single usage
usage/:id 		DELETE 		DELETE 		Delete a single usage
"""
print("Starting api round trip test, creating user, getting auth token")
# Make a user and get an auth token for them
user = {'username': 'planetly', 'password1': 'zerocarbon', 'password2': "zerocarbon"}
r = requests.post('http://localhost:8000/signup/',
	data=user)
user = {'username': 'planetly', 'password': 'zerocarbon'}
r = requests.post('http://localhost:8000/api-token-auth/',
	data=user)
assert r.status_code== 200
data = r.json()
# We will use this header to authenticate all of our following requests
headers = {'Authorization': 'Token %s' % data['token']}

####
#
# Sequentially call every CRUD api route listed above
# The calls are in the following order:
# create usage_type, update usage_type, get (single) usage_type, create usage, get (all) usage,
# update usage get (single) usage, delete usage, delete usage_type, get (all) usage_type
#
###

# TEST CREATE usage_type
usage_type_data={"name": "driving", "unit":"miles"}
r = requests.post('http://localhost:8000/carbon_usage/usage_type/',
	headers=headers, data=usage_type_data)
assert r.status_code==201
driving_usage_type = r.json()
driving_usage_type_id = driving_usage_type['id']

# TEST UPDATE usage_type
usage_type_data={"name": "driving", "unit":"kilometers"}
r = requests.put('http://localhost:8000/carbon_usage/usage_type/%s/' % driving_usage_type_id,
	headers=headers, data=usage_type_data)
assert r.status_code==200
# Update driving_usage_type with updated value
driving_usage_type = r.json()

# Test GET (single) usage_type
r = requests.get('http://localhost:8000/carbon_usage/usage_type/%s/' % driving_usage_type_id,
	headers=headers)
assert r.status_code==200
assert r.json() == driving_usage_type

# TEST CREATE usage
creation_date=datetime.now()
timezone = pytz.timezone('Europe/Berlin')
aware_datetime = timezone.localize(creation_date)
creation_date = aware_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f%z")
creation_date = creation_date[:-2]+":00"

####
# A note on timezone string formatting
#
# django stores timezone aware datetimes in the following form: 2021-04-05T18:55:06.212829+02:00
# strftime does not include an option for a colon between hours and minutes of timezone offset
# https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
# see the section for %z

# thus this mess is neccessary to get a string matching djangos representation
# Would get to the bottom of this if I had more time!
####

usage_data={"usage_type": driving_usage_type_id, "usage_at":creation_date}
r = requests.post('http://localhost:8000/carbon_usage/usage/',
	headers=headers, data=usage_data)
usage_data = r.json()
usage_id = usage_data['id']
assert r.status_code==201
assert usage_data['user']=='planetly'
assert usage_data['usage_type']==driving_usage_type_id
assert usage_data['usage_at']==creation_date

# Test GET (all) usage
r = requests.get('http://localhost:8000/carbon_usage/usage/',
	headers=headers)
assert r.status_code==200
all_usage_data = r.json()
# Test pagination information is included
assert 'count' in all_usage_data
assert 'previous' in all_usage_data
assert 'next' in all_usage_data
assert usage_data in all_usage_data['results']

# Test update usage
usage_data={"usage_type": driving_usage_type_id, "usage_at":datetime.now()}
r = requests.put('http://localhost:8000/carbon_usage/usage/%s/' % usage_id,
	headers=headers, data=usage_data)
assert r.status_code==200
usage_data = r.json()

# test GET (single) usage
r = requests.get('http://localhost:8000/carbon_usage/usage/%s/' % usage_id,
	headers=headers)
assert r.status_code==200
assert r.json() == usage_data

# Test DELETE usage
r = requests.delete('http://localhost:8000/carbon_usage/usage/%s/' % usage_id,
	headers=headers, data=usage_type_data)
assert r.status_code == 204

# Test DELETE usage_type
r = requests.delete('http://localhost:8000/carbon_usage/usage_type/%s/' % driving_usage_type_id,
	headers=headers)
assert r.status_code == 204

# Test GET (all) usage_type
r = requests.get('http://localhost:8000/carbon_usage/usage_type/',
	headers=headers)
assert r.status_code==200
assert driving_usage_type not in r.json()['results']

print("Tested happy path of CRUD calls for usage/usagetype successfully!")
