from django.core.management.base import BaseCommand

import sys

import productstatus.core.models
import productstatus.check
import productstatus.check.models


class UnknownCheckException(Exception):
    pass


class Printer(object):
    def format(self, result):
        raise NotImplementedError('Please implement the "print" command.')

    def print(self, result):
        print(self.format(result))


class StdoutPrinter(Printer):
    def format(self, result):
        return '%s - %s' % (result.get_code()[1], result.get_failing_message())


class MultiStdoutPrinter(StdoutPrinter):
    def format(self, result):
        return '%s: %s' % (result.check.name, super(MultiStdoutPrinter, self).format(result))


class Command(BaseCommand):
    help = 'Run one or all product checks, verifying that ProductInstances are added to the database according to their schedule'

    def add_arguments(self, parser):
        parser.add_argument('check_name', nargs='?', type=str)
        parser.add_argument('--list', action='store_true', required=False)

    def print_check_list(self):
        checks = list(productstatus.check.models.Check.objects.all().order_by('name'))
        for check in checks:
            print(check.name)

    def handle(self, *args, **options):
        if options['list'] is True:
            self.print_check_list()
            sys.exit(0)

        try:
            if options['check_name']:
                try:
                    objects = [productstatus.check.models.Check.objects.get(name=options['check_name'])]
                    printer = StdoutPrinter()
                except:
                    raise UnknownCheckException('UNKNOWN - Check not found: %s' % options['check_name'])
            else:
                objects = list(productstatus.check.models.Check.objects.all())
                printer = MultiStdoutPrinter()

        except UnknownCheckException as e:
            print(e)
            sys.exit(productstatus.check.UNKNOWN[0])

        max_severity = productstatus.check.OK
        for check in objects:
            result = check.execute()
            max_severity = max(max_severity, result.get_code())
            printer.print(result)
        sys.exit(max_severity[0])
