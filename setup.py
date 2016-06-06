try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'Productstatus',
    'author': 'MET Norway',
    'url': 'https://github.com/metno/productstatus',
    'download_url': 'https://github.com/metno/productstatus',
    'author_email': 'it-geo-tf@met.no',
    'version': '1.0',
    'install_requires': [
        'Django==1.9.5',
        'django-extensions==1.5.9',
        'django-mptt==0.7.4',
        'django-tastypie==0.13.3',
        'django-cors-headers==1.1.0',
        'ipython==4.2.0',
        'kafka-python==1.1.1',
        'python-dateutil==2.5.3',
        'psycopg2==2.6.1',
        'raven==5.16.0',
    ],
    'packages': [],
    'scripts': [],
    'name': 'productstatus'
}

setup(**config)
