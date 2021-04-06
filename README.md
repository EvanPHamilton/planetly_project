Hello Planetly this is the readme for Evan Hamilton's project.

I will go through how to set up the app, how to interact with the app,
describe the api I created, and then give my thoughts and notes
on the project.

#####
#
# Setup
#
#####

I wrote my project using django, django-rest-framework, docker and docker compose. Docker and docker-compose will need to be installed on the system
where you would like to run this, everything else will be installed
by docker!

To run the project, you should be able to simply execute the following commands.

First, if you are on linux you will then need to run:

`sudo chown -R $USER .`

This will give your user accout permission to execute the dockerfiles.

Secondly:

`docker-compose -f docker-compose.yml up --build -d`
This can take some time as we are building the docker image

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
`docker-compose exec web /usr/local/bin/python manage.py test`
to run the django tests I wrote

Or you can run
`docker-compose exec web /usr/local/bin/python api_tests.py` 
to run a python script, testing out the api routes. 
A note on this test script. This ran without trouble on ubuntu 18.04.
When setting up this repo from scrath on a mac, the first time I ran the script it failed with a networkign issue. 
I had to run `docker-compose down` and `docker-compose up` again to get this script to run successfully.

Or you can navigate to 'https://127.0.0.1:8000'
to check out the minimal front end I wrote for the app.
This only consists of login pages, plus what is provided by
the django rest framework.

Finally, you can test the api manually using curl, 
although the endpoints are protected with an auth token
generated on a per user basis. I ran out of time to implement 
JWT tokens, or a more sensible session based authentication paradigm. 
But the api_tests.py file contains an example of programatically
creating a user and generating an auth token. 

#####
#
# API SPECS
#
#####

There are two primary api endpoints

`/carbon_usage/usage`

`/carbon_usage/usage_type`

Corresponding to the usage and usage_type datamodels
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
# usage filtering and sorting
#
#####

For the `/usage/` endpoint you can sort on either 
the `usage_at` or `usage_type` parameter, encoded
as a url parameter as follows:
`/carbon_usage/usage/?ordering=-usage_type`

Note the `-` in front of usage_type. This returns
the result in descending order. If the `-` is not
included, the results will be returned in ascending order.
The same can be done for the usage_at parameter.
Ascending order is the default.

Furthermore, the `/usage/` endpoint supports two more
optional parameters `timerange_start` and `timerange_end`,
these allow for filtering for /usage/ entries after or before
the respective timeranges, which should be passed as datetimes.
An example valid datetime is: `2021-04-06 18:59:39.5775290`

These parameters can be used individually, or together. 

#####
#
# usage_type filtering and sorting
#
#####
For the `/usage/usage_type` endpoint you can sort on either 
the `unit` or `name` parameters, encoded
as a url parameter as follows:
`/carbon_usage/usage_type/?ordering=-name`

The same scheme with `-` applies, to allow returning
in desecending order.

#####
#
# Notes on this project
#
#####
Hey Planetly team, per your last set of requirements I am giving a bit of a description of my experience.

This definitely took me longer than 2-4 hours to complete. I worked on over three days, for a couple hours each time. I over-estimated how much of django I remembered, and spent a good chunk of time re-familiarizing myself with it. Django provides so much and so many ways to do the same thing, I spent a lot of time wading through trying to understand the `django` way to do something. I think I could have done this whole project in flask in 4 hours, but ultimately you are looking for a django developer so I think it's good I read up. To be honest I don't have any strong opinions on how django code should be organized, so I would look forward to working with people who have more experience with the framework.

If I had had more time, I would have liked to spend some more time providing docs, writing cleaner code, and implementing a token based auth system. Unfortunately, I spent most of my time reading through django docs. Great learning experience, but I was left feeling like I did not get to demonstrate as much of my software engineering experience as I wanted.


The one major painpoint for me was django's handling of timezones. I originally updated my django settings to be timezone aware and to use Berlin's timezone. My gut instinct is to always store datetimes in the db in UNIX time and handle the timezones myself. It seems django is trying to abstract some of that complexity away from me, and I got a bit hung up on this, specifically django parsing timezone aware datetime strings -- so I ended up with some unpleasant string manipulation. I promise that would never make it into production!

Lastly, most of my test coverage ended up covering features that django baked in. I think these tests would have made more sense if I was doing things like pagination manually. Maybe they are redundant and my test coverage time would have been better spent elsewhere, that is a lesson for the next time I use django! I use requests a lot to quickly test things personally, so I also wrote a small python script to test the api from the outside, using the requests library to validate the api routes. This was more a personal sanity check, though in production I would consider running a more robust version of this script nightly as part of a CI/CD system.

Other than that, I think it mostly went well! Looking forward to hearing from you all!

Cheers

Evan