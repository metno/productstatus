# Modelstatus

Modelstatus is a persistent storage for weather model metadata and run-time information. It provides a REST API for data retrieval and manipulation.

## Setting it up

1. Checkout the source code from https://github.com/metno/modelstatus.git

2. (Optional, recommended:) set up a virtual environment for the Modelstatus python packages and their dependencies:

    $ cd modelstatus
    $ virtualenv deps
    $ . deps/bin/activate

3. Install the Modelstatus dependencies:

    $ pip install -r requirements.txt

## Running

You should always update the database schemas to the latest version after upgrading:

    $ ./manage.py migrate

Running a development server is as simple as:

    $ ./manage.py runserver

Now you can access the application at http://localhost:8000.

The API is HATEOAS-enabled, and available at http://localhost:8000/api/v1/.

There is also an administration interface available at http://localhost:8000/admin/.

You can create a superuser by running:

    $ ./manage.py createsuperuser
