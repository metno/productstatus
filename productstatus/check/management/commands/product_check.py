from django.core.management.base import BaseCommand

import sys

import productstatus.core.models
import productstatus.check
import productstatus.check.models


class UnknownCheckException(Exception):
    pass


class Command(BaseCommand):
    help = 'Run one or all product checks, verifying that ProductInstances are added to the database according to their schedule'

    def add_arguments(self, parser):
        parser.add_argument('check_name', nargs='?', type=str)
        parser.add_argument('--list', action='store_true', required=True)

    def handle(self, *args, **options):
        if options['list']:
            checks = list(productstatus.check.models.Check.objects.all().order_by('name'))
            for check in checks:
                print(check.name)
            sys.exit(0)

        try:
            if options['check_name']:
                try:
                    objects = [productstatus.check.models.Check.objects.get(name=options['check_name'])]
                except:
                    raise UnknownCheckException('UNKNOWN - Check not found: %s' % options['check_name'])
            else:
                objects = list(productstatus.check.models.Check.objects.all())
        except UnknownCheckException as e:
            print(e)
            sys.exit(productstatus.check.UNKNOWN[0])

        max_severity = productstatus.check.OK
        for check in objects:
            result = check.execute()
            max_severity = max(max_severity, result.get_code())
            self.print_result(result, multi=not bool(options['check_name']))
        sys.exit(max_severity[0])

    def print_result(self, result, multi=False):
        if multi:
            print('%s: %s - %s' % (result.check.name, result.get_code()[1], result.get_failing_message()))
        else:
            print('%s - %s' % (result.get_code()[1], result.get_message()))
