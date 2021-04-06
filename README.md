Hello Planetly this is the readme for Evan Hamilton's project.

I will go through how to set up the app, how to interact with the app,
describe the api I created, and then give my thoughts and notes
on the project.

#####
#
# Setup
#
#####

I wrote my project using django, django-rest-framework, docker and docker compose.

To run the project, you should be able to simply execute:

First: 
`docker-compose -f docker-compose.yml up --build -d`

Then, if you are on linux you will need to run:
`sudo chown -R $USER .`
to give docker permission to run the docker files. 
This should not be a problem on mac osx/windows.

Then run 
`docker-compose up`

To start the application.

The first time you run `docker-compose up` you will have to run:

`docker-compose exec web /usr/local/bin/python manage.py migrate `
from a separate terminal, in order to run the database migrations.

From there you have everything up and running!

#####
#
# Interacting with the app
#
#####

There are four things you can do from there

First, you can run
`docker-compose exec web /usr/local/bin/python manage.py tests`
to run the django tests I wrote

Or you can run
`python api_tests.py` 
to run a python script, testing out the api routes. 

Or you can navigate to 'https://127.0.0.1:8000'
to check out the minimal front end I wrote for the app.
This only consists of login pages, plus what is provided by
the django rest framework.

Finally, you can test the api manually using curl, 
although the endpoints are protected with an auth token
generated on a per user basis. I ran out of time to implement 
JWT tokens, or a more sensible session based authentication paradigm. 

#####
#
# API SPECS
#
#####

There are two primary api endpoints

/carbon_usage/usage
/carbon_usage/usage_type

corresponding to the usage and usage_type datamodels
described in the prompt. I used django's user model 
rather than rolling my own. There are a number of other
api endpoints for django's admin app, authentication,
and token generation, these can be seen in the 
`planety_app` urls.py file, but are not of primary interest.

Both usage and usage_type support all CRUD commands

POST   /usage_type/     -- CREATE
GET    /usage_type/     -- READ
GET    /usage_type/:id  -- READ all
PUT    /usage_type/:id  -- UPDATE
PATCH  /usage_type/:id  -- PARTIAL UPDATE
DELETE /usage_type/:id  -- DELETE

POST   /usage_type/     -- CREATE
GET    /usage_type/     -- READ
GET    /usage_type/:id  -- READ all
PUT    /usage_type/:id  -- UPDATE
PATCH  /usage_type/:id  -- PARTIAL UPDATE
DELETE /usage_type/:id  -- DELETE

#####
#
# Filtering, sorting, pagination
#
#####

The GET /usage_type/ and GET /usage/ endpoints
also support pagination, filtering and sorting.
Pagination occurs by default, with 10 values per page.

#####
#
# usage 
#
#####

For the /usage/ endpoint you can sort on either 
the 'usage_at' or 'usage_type' parameter, encoded
as a url parameter as follows:
/carbon_usage/usage/?ordering=-usage_type

Note the `-` in front of usage_type. This returns
the result in descending order. If the `-` is not
included, the results will be returned in ascending order.
The same can be done for the usage_at parameter.
Ascending order is the default.

Furthermore, the /usage/ endpoint supports two more
optional parameters `timerange_start` and `timerange_end`,
these allow for filtering for /usage/ entries after or before
the respective timeranges, which should be passed as datetimes.
An example valid datetime is: `2021-04-06 18:59:39.5775290`

These parameters can be used individually, or together. 

#####
#
# usage_type
#
#####
For the /usage/usage_type endpoint you can sort on either 
the 'unit', 'name' parameter, encoded
as a url parameter as follows:
/carbon_usage/usage_type/?ordering=-name

The same scheme with `-` applies, to allow returning
in desecending order.

