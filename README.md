# Productstatus

## Abstract

Productstatus is a persistent storage for weather product metadata and run-time information. It provides a REST API for data retrieval and manipulation.

![Graphical representation of data model]
(doc/model_graph.png)

## Setting it up

1. Checkout the source code from https://github.com/metno/productstatus.git

2. (Optional, recommended:) set up a virtual environment for the Productstatus python packages and their dependencies:

    $ cd productstatus
    $ virtualenv deps
    $ . deps/bin/activate

3. Install ZeroMQ dev libraries. You need at least version 3.0:

    $ sudo apt-get install libzmq-dev build-essential python-dev libpq-dev

4. Install the Productstatus dependencies:

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

## Running tests

    ./manage.py test productstatus.core.tests

## Setting up API user permissions

You must grant write access to the certain models required for your API user. This can be done by editing users through the Django administration interface.

For `add` access, it is neccessary to define `change` access as well. This is reported as a bug upstream: https://github.com/django-tastypie/django-tastypie/issues/1391

## Generating the data model graph

```
$ ./manage.py graph_models core -x created,modified | dot -Tpng > doc/model_graph.png
```

## Required parameters for a product instance

In order to post information about a product instance, you'll need the following information:

### Product

A //Product// is a data set definition. It defines who is responsible, the bounding box, projection, grid resolution, number of time steps, and also includes references to names in other metadata systems such as WDB. The Product can be created from the Django administration interface, and retrieved using the API.

### Reference time

The start date and time, including time zone, for the product's prognosis.

### Dataset version

In most cases, this can be set to `1`. In case upstream product generation fails, and a re-run has been done, this number must be increased, in order to indicate to clients that a newer data set exists.

### Data format

Each file produced during product generation has its specific data format, for instance GRIB or NetCDF. This data format must be reported to Productstatus. Data formats can be managed from the Django administration interface, and retrieved using the API.

### Service backend

A data file must reside somewhere. Information about how data can be retrieved, is stored in a service backend object. Each data file must report which service backend it is available from. These can be managed from the Django administration interface, and retrieved using the API.

### Expiry time

If a data file is not to be stored permanently, its exact end-of-life time, including time zone, must be reported.

### URL

Each data file must have an URL, from which it can be retrieved until its expiry time.

## An example of posting a product instance and its data set

This example is illustrated using [httpie](https://pypi.python.org/pypi/httpie).

Imagine an instance of the product //Arome MetCoOp 2500m// has been generated, its reference time is //2015-10-29T00:00:00Z//, and the resulting data set is a //NetCDF// file which we have placed on our imaginary file servers //Datastore1// and //Datastore2//.

How do we know which //Product// resource to reference? In a lot of cases, this value could be hard-coded into your configuration, since the UUID will not change. But you could also filter the Product resource collection to figure it out dynamically, for instance by searching for the WDB data provider name:

    $ http GET http://localhost:8000/api/v1/product/?wdb_data_provider=arome_metcoop_2500m

    HTTP/1.0 200 OK
    Cache-Control: no-cache
    Content-Type: application/json
    Date: Thu, 29 Oct 2015 10:02:52 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Vary: Accept
    X-Frame-Options: SAMEORIGIN

    {
        "meta": {
            "limit": 20,
            "next": null,
            "offset": 0,
            "previous": null,
            "total_count": 1
        },
        "objects": [
            {
                "bounding_box": "0,0,0,0",
                "created": "2015-10-28T16:18:30.704007",
                "grid_resolution": "2500.00000",
                "grid_resolution_unit": "m",
                "id": "66340f0b-2c2c-436d-a077-3d939f4f7283",
                "modified": "2015-10-28T16:18:31.823996",
                "name": "AROME MetCoOp 2500m",
                "parent": null,
                "prognosis_length": 66,
                "resource_uri": "/api/v1/product/66340f0b-2c2c-436d-a077-3d939f4f7283/",
                "time_steps": 66,
                "wdb_data_provider": "arome_metcoop_2500m"
            }
        ]
    }

Now that we have a resource URI for the product, we can go ahead and POST our product instance:

    $ http --json POST http://localhost:8000/api/v1/productinstance/ \
        product=/api/v1/product/66340f0b-2c2c-436d-a077-3d939f4f7283/ \
        reference_time=2015-10-29T00:00:00Z \
        version=1

    HTTP/1.0 201 CREATED
    Content-Type: text/html; charset=utf-8
    Date: Thu, 29 Oct 2015 10:10:25 GMT
    Location: http://localhost:8000/api/v1/productinstance/4e3ddbd0-a7e1-40cd-bef9-6ab55e0352a7/
    Server: WSGIServer/0.1 Python/2.7.3
    Vary: Accept
    X-Frame-Options: SAMEORIGIN

We can inspect our newly created product instance resource:

    $ http GET http://localhost:8000/api/v1/productinstance/4e3ddbd0-a7e1-40cd-bef9-6ab55e0352a7/

    HTTP/1.0 200 OK
    Cache-Control: no-cache
    Content-Type: application/json
    Date: Thu, 29 Oct 2015 10:13:05 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Vary: Accept
    X-Frame-Options: SAMEORIGIN

    {
        "created": "2015-10-29T10:10:25.858306",
        "id": "4e3ddbd0-a7e1-40cd-bef9-6ab55e0352a7",
        "product": "/api/v1/product/66340f0b-2c2c-436d-a077-3d939f4f7283/",
        "modified": "2015-10-29T10:10:25.858340",
        "reference_time": "2015-10-29T00:00:00",
        "resource_uri": "/api/v1/productinstance/4e3ddbd0-a7e1-40cd-bef9-6ab55e0352a7/",
        "version": 1
    }

Now, lets post some files. We know that our data set contains 66 hours of data, and it is stored in a single file. We must first post information about which time period our data set spans, and optionally, which parameters it contains:

    $ http --json POST http://localhost:8000/api/v1/data/ \
        productinstance=/api/v1/productinstance/4e3ddbd0-a7e1-40cd-bef9-6ab55e0352a7/ \
        time_period_begin=2015-10-29T00:00:00Z \
        time_period_end=2015-10-31T18:00:00Z

    HTTP/1.0 201 CREATED
    Content-Type: text/html; charset=utf-8
    Date: Thu, 29 Oct 2015 10:17:28 GMT
    Location: http://localhost:8000/api/v1/data/8c381dc4-7d09-4edd-ae58-39715d04397c/
    Server: WSGIServer/0.1 Python/2.7.3
    Vary: Accept
    X-Frame-Options: SAMEORIGIN

The newly created object is a canonical and immutable representation of the data set and its parameters. As data files can have several formats and locations, they are contained within another resource. Lets inspect the newly created object:

    $ http GET http://localhost:8000/api/v1/data/8c381dc4-7d09-4edd-ae58-39715d04397c/

    HTTP/1.0 200 OK
    Cache-Control: no-cache
    Content-Type: application/json
    Date: Thu, 29 Oct 2015 10:18:30 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Vary: Accept
    X-Frame-Options: SAMEORIGIN

    {
        "created": "2015-10-29T10:17:28.299035",
        "id": "8c381dc4-7d09-4edd-ae58-39715d04397c",
        "productinstance": "/api/v1/productinstance/4e3ddbd0-a7e1-40cd-bef9-6ab55e0352a7/",
        "modified": "2015-10-29T10:17:28.299048",
        "resource_uri": "/api/v1/data/8c381dc4-7d09-4edd-ae58-39715d04397c/",
        "time_period_begin": "2015-10-29T00:00:00",
        "time_period_end": "2015-10-31T18:00:00"
    }

We must connect our data files to three separate resource URIs: the newly created data resource, a data format, and a service backend. Let's inspect our API for the latter two:

    $ http GET http://localhost:8000/api/v1/data_format/

    HTTP/1.0 200 OK
    Cache-Control: no-cache
    Content-Type: application/json
    Date: Thu, 29 Oct 2015 10:23:45 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Vary: Accept
    X-Frame-Options: SAMEORIGIN

    {
        "meta": {
            "limit": 20,
            "next": null,
            "offset": 0,
            "previous": null,
            "total_count": 1
        },
        "objects": [
            {
                "created": "2015-10-28T16:18:23.511871",
                "id": "d921b282-b4b1-435f-b7e8-2b58daa8a0ff",
                "modified": "2015-10-29T09:09:06.172335",
                "name": "netcdf",
                "resource_uri": "/api/v1/data_format/d921b282-b4b1-435f-b7e8-2b58daa8a0ff/"
            }
        ]
    }

    $ http GET http://localhost:8000/api/v1/service_backend/

    HTTP/1.0 200 OK
    Cache-Control: no-cache
    Content-Type: application/json
    Date: Thu, 29 Oct 2015 10:24:23 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Vary: Accept
    X-Frame-Options: SAMEORIGIN

    {
        "meta": {
            "limit": 20,
            "next": null,
            "offset": 0,
            "previous": null,
            "total_count": 2
        },
        "objects": [
            {
                "created": "2015-10-28T16:18:40.104098",
                "documentation_url": "file:///dev/null"
                "id": "f314a536-bb96-4d2a-83cd-9764e2e3e16a",
                "modified": "2015-10-28T16:18:41.152094",
                "name": "Datastore1",
                "resource_uri": "/api/v1/service_backend/f314a536-bb96-4d2a-83cd-9764e2e3e16a/"
            },
            {
                "created": "2015-10-28T16:18:40.104098",
                "documentation_url": "file:///dev/null"
                "id": "ee3a5890-f31f-4dbc-ad3d-6df06370d271",
                "modified": "2015-10-28T16:18:41.152094",
                "name": "Datastore2",
                "resource_uri": "/api/v1/service_backend/ee3a5890-f31f-4dbc-ad3d-6df06370d271/"
            }
        ]
    }

Our fictional data is stored in NetCDF format on both //Datastore1// and //Datastore2//. Let's create an entry for each of them:

    $ http --json POST http://localhost:8000/api/v1/data_file/ \
        data=/api/v1/data/8c381dc4-7d09-4edd-ae58-39715d04397c/ \
        format=/api/v1/data_format/d921b282-b4b1-435f-b7e8-2b58daa8a0ff/ \
        service_backend=/api/v1/service_backend/f314a536-bb96-4d2a-83cd-9764e2e3e16a/ \
        url=https://datastore1/arome_metcoop_2500m_2015-10-29T00:00:00Z.nc

    HTTP/1.0 201 CREATED
    Content-Type: text/html; charset=utf-8
    Date: Thu, 29 Oct 2015 11:57:22 GMT
    Location: http://localhost:8000/api/v1/data_file/1fbfe789-2b77-442f-a676-3304f60ea88e/
    Server: WSGIServer/0.1 Python/2.7.3
    Vary: Accept
    X-Frame-Options: SAMEORIGIN

    $ http --json POST http://localhost:8000/api/v1/data_file/ \
        data=/api/v1/data/8c381dc4-7d09-4edd-ae58-39715d04397c/ \
        format=/api/v1/data_format/d921b282-b4b1-435f-b7e8-2b58daa8a0ff/ \
        service_backend=/api/v1/service_backend/ee3a5890-f31f-4dbc-ad3d-6df06370d271/ \
        url=https://datastore2/arome_metcoop_2500m_2015-10-29T00:00:00Z.nc

    HTTP/1.0 201 CREATED
    Content-Type: text/html; charset=utf-8
    Date: Thu, 29 Oct 2015 11:57:22 GMT
    Location: http://localhost:8000/api/v1/data_file/71f5a9b6-4c86-4723-86d5-f08a2f1fd686/
    Server: WSGIServer/0.1 Python/2.7.3
    Vary: Accept
    X-Frame-Options: SAMEORIGIN

Finally, we can access these newly created data file resources by searching for them:

    $ http GET http://localhost:8000/api/v1/data_file/?data=8c381dc4-7d09-4edd-ae58-39715d04397c

    HTTP/1.0 200 OK
    Cache-Control: no-cache
    Content-Type: application/json
    Date: Thu, 29 Oct 2015 12:01:35 GMT
    Server: WSGIServer/0.1 Python/2.7.3
    Vary: Accept
    X-Frame-Options: SAMEORIGIN

    {
        "meta": {
            "limit": 20,
            "next": null,
            "offset": 0,
            "previous": null,
            "total_count": 2
        },
        "objects": [
            {
                "created": "2015-10-29T11:57:22.000802",
                "data": "/api/v1/data/8c381dc4-7d09-4edd-ae58-39715d04397c/",
                "expires": null,
                "format": "/api/v1/data_format/d921b282-b4b1-435f-b7e8-2b58daa8a0ff/",
                "id": "1fbfe789-2b77-442f-a676-3304f60ea88e",
                "modified": "2015-10-29T11:57:22.000821",
                "resource_uri": "/api/v1/data_file/1fbfe789-2b77-442f-a676-3304f60ea88e/",
                "service_backend": "/api/v1/service_backend/f314a536-bb96-4d2a-83cd-9764e2e3e16a/",
                "url": "https://datastore1/arome_metcoop_2500m_2015-10-29T00:00:00Z.nc"
            },
            {
                "created": "2015-10-29T11:59:02.795433",
                "data": "/api/v1/data/8c381dc4-7d09-4edd-ae58-39715d04397c/",
                "expires": null,
                "format": "/api/v1/data_format/d921b282-b4b1-435f-b7e8-2b58daa8a0ff/",
                "id": "71f5a9b6-4c86-4723-86d5-f08a2f1fd686",
                "modified": "2015-10-29T11:59:02.795449",
                "resource_uri": "/api/v1/data_file/71f5a9b6-4c86-4723-86d5-f08a2f1fd686/",
                "service_backend": "/api/v1/service_backend/ee3a5890-f31f-4dbc-ad3d-6df06370d271/",
                "url": "https://datastore2/arome_metcoop_2500m_2015-10-29T00:00:00Z.nc"
            }
        ]
    }
