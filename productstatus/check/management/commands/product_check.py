from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection

import sys
import json
import socket
import requests
import logging

import django.db.utils

import productstatus.core.models
import productstatus.check
import productstatus.check.models


class UnknownCheckException(Exception):
    pass


class Printer(object):
    def format(self, result):
        raise NotImplementedError('Please implement the "format" command.')

    def print(self, result):
        print(self.format(result))
        return 1


class StdoutPrinter(Printer):
    def format(self, result):
        return '%s - %s' % (result.get_code()[1], result.get_failing_message())


class MultiStdoutPrinter(StdoutPrinter):
    def format(self, result):
        return '%s: %s' % (result.check.name, super(MultiStdoutPrinter, self).format(result))


class SensuPrinter(Printer):
    def __init__(self, handlers=[]):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.handlers = handlers

    def format(self, result):
        data = {
            'name': result.check.name,
            'output': result.get_failing_message(),
            'status': result.get_code()[0],
            'handlers': self.handlers,
        }
        return json.dumps(data)

    def print(self, result):
        payload = self.format(result)
        self.sock.sendto(payload.encode('ascii'), ('127.0.0.1', 3030))
        return 1


class PagerDutyPrinter(Printer):
    """
    Submit a check result to PagerDuty.
    """
    def format(self, result):
        # No PagerDuty connection, ignore
        if len(result.check.pagerduty_service) == 0:
            return None

        # Generate exploration URL so that users can drill down into the error.
        url = "%s://%s/explore/?q=%s" % (settings.PRODUCTSTATUS_PROTOCOL,
                                         settings.PRODUCTSTATUS_HOST,
                                         result.check.product.id)

        # Create a payload, defaulting to trigger new incident.
        payload = {
            'client': 'Productstatus',
            'client_url': url,
            'description': 'Integrity check failed',
            'details': result.messages(),
            'event_type': 'trigger',
            'incident_key': result.check.pagerduty_incident,
            'service_key': result.check.pagerduty_service,
        }

        # OK conditions result in a resolve event if we have an incident key.
        if result.get_code() == productstatus.check.OK:
            if len(result.check.pagerduty_incident) == 0:
                return None
            payload['event_type'] = 'resolve'

        return payload


    def print(self, result):
        # Ignore empty payloads
        payload = self.format(result)
        if payload is None:
            return 0

        # Post to PagerDuty
        pagerduty_session = requests.Session()
        pagerduty_session.headers.update({
            'Authorization': 'Token token=' + settings.PAGERDUTY_API_KEY,
            'Accept': 'application/vnd.pagerduty+json;version=2'
        })
        r = pagerduty_session.post('https://events.pagerduty.com/generic/2010-04-15/create_event.json',
                                   data=json.dumps(payload))

        # Fail on error statuses
        response = r.json()
        if r.status_code < 200 or r.status_code >= 300:
            raise Exception(response)

        # We should receive an incident key from PagerDuty.
        if payload['event_type'] == 'trigger':
            if 'incident_key' not in response:
                raise Exception('Did not get incident key in response from PagerDuty.')
            result.check.pagerduty_incident = response['incident_key']

        # In case of a resolved incident, reset the incident key.
        elif payload['event_type'] == 'resolve':
            result.check.pagerduty_incident = None

        # Persist the incident key.
        result.check.save()

        return 1


class Command(BaseCommand):
    help = 'Run one or all product checks, verifying that ProductInstances are added to the database according to their schedule'

    def add_arguments(self, parser):
        parser.add_argument('check_name', nargs='?', type=str)
        parser.add_argument('--list', action='store_true', required=False, help='List all available checks')
        parser.add_argument('--sensu', action='store_true', required=False, help='Send check output to a local Sensu client instead of stdout')
        parser.add_argument('--sensu-handlers', nargs='*', metavar='HANDLER', help='Define which Sensu handlers to add to check outputs')
        parser.add_argument('--pagerduty', action='store_true', required=False, help='Enable PagerDuty output')
        parser.add_argument('--ignore-read-only', action='store_true', required=False, help='Suppress check output if the database is read-only')

    def read_only(self):
        query = 'SELECT pg_is_in_recovery()'
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return bool(cursor.fetchone()[0])
        except django.db.utils.OperationalError:
            # thrown e.g. when this is not a PostgreSQL database
            sys.stderr.write("WARNING: ignoring database error while running query '%s'; assuming RW database\n" % query)
            return False

    def print_check_list(self):
        checks = list(productstatus.check.models.Check.objects.all().order_by('name'))
        for check in checks:
            print(check.name)

    def handle(self, *args, **options):
        if options['list'] is True:
            self.print_check_list()
            sys.exit(0)

        # Collect check results
        try:
            if options['check_name']:
                try:
                    printer = StdoutPrinter()
                    check = productstatus.check.models.Check.objects.get(name=options['check_name'])
                    results = [check.execute()]
                    num_checks = 1
                except:
                    raise UnknownCheckException('Check not found: %s' % options['check_name'])
            else:
                num_checks = 0
                printer = MultiStdoutPrinter()
                objects = list(productstatus.check.models.Check.objects.all())
                results = []
                for check in objects:
                    result = check.execute()
                    result.check = check
                    results += [result]
                    num_checks += 1

        except UnknownCheckException as e:
            results = [productstatus.check.SimpleCheckResult(productstatus.check.UNKNOWN, str(e))]
            results[0].check = type("Foo", (object,), {})()
            results[0].check.name = options['check_name']

        if options['ignore_read_only'] and self.read_only():
            print('%d check results have been ignored because the database is in read-only mode' % num_checks)
            return
        elif options['sensu'] is True:
            printer = SensuPrinter(handlers=options['sensu_handlers'])
        elif options['pagerduty'] is True:
            printer = PagerDutyPrinter()

        # Send or print results
        try:
            submitted = 0
            max_severity = productstatus.check.OK
            for result in results:
                max_severity = max(max_severity, result.get_code())
                submitted += printer.print(result)
        except Exception as e:
            print('Check printer failed with exception:', e)
            sys.exit(255)

        if options['sensu']:
            print('%d check results have been submitted to Sensu' % submitted)
        elif options['pagerduty']:
            print('%d check results have been submitted to PagerDuty' % submitted)
        else:
            sys.exit(max_severity[0])
