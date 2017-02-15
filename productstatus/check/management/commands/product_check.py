from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection

import sys
import json
import socket

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


class StdoutPrinter(Printer):
    def format(self, result):
        return '%s - %s' % (result.get_code()[1], result.get_failing_message())


class MultiStdoutPrinter(StdoutPrinter):
    def format(self, result):
        return '%s: %s' % (result.check.name, super(MultiStdoutPrinter, self).format(result))


class SensuPrinter(Printer):
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def format(self, result):
        data = {
            'name': result.check.name,
            'output': result.get_failing_message(),
            'status': result.get_code()[0],
        }
        return json.dumps(data)

    def print(self, result):
        payload = self.format(result)
        self.sock.sendto(payload.encode('ascii'), ('127.0.0.1', 3030))


class Command(BaseCommand):
    help = 'Run one or all product checks, verifying that ProductInstances are added to the database according to their schedule'

    def add_arguments(self, parser):
        parser.add_argument('check_name', nargs='?', type=str)
        parser.add_argument('--list', action='store_true', required=False, help='List all available checks')
        parser.add_argument('--sensu', action='store_true', required=False, help='Send check output to a local Sensu client instead of stdout')
        parser.add_argument('--ignore-read-only', action='store_true', required=False, help='Suppress check output if the database is read-only')

    def read_only(self):
        query = 'SELECT pg_is_in_recovery()'
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                return bool(cursor.fetchone())
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
            printer = SensuPrinter()

        # Send or print results
        max_severity = productstatus.check.OK
        for result in results:
            max_severity = max(max_severity, result.get_code())
            printer.print(result)

        if options['sensu'] is not True:
            sys.exit(max_severity[0])
        else:
            print('%d check results have been submitted to Sensu' % num_checks)
