import productstatus.check.exceptions


# Standard Nagios error codes
OK = (0, 'OK',)
WARNING = (1, 'WARNING',)
CRITICAL = (2, 'CRITICAL',)
UNKNOWN = (3, 'UNKNOWN',)


class CheckResult(object):
    def __init__(self):
        self.parts = []

    def add_part(self, part):
        self.parts += [part]

    def get_parts(self):
        return self.parts

    def get_code(self):
        return max([x.code for x in self.get_parts()])

    def get_message(self):
        return '; '.join([x.message for x in self.get_parts()])

    def get_failing_message(self):
        failing_parts = []
        for part in self.get_parts():
            if part.code > OK:
                failing_parts += [part]
        if len(failing_parts) == 0:
            return 'All tests pass'
        return '; '.join([x.message for x in failing_parts])


class SimpleCheckResult(CheckResult):
    def __init__(self, code, message):
        super(SimpleCheckResult, self).__init__()
        part = CheckResultPart()
        part.set_result(code, message)
        self.add_part(part)


class CheckResultPart(object):
    def __init__(self):
        self.code = None
        self.message = None

    def set_result(self, code, message):
        self.code = code
        self.message = message

    def get_result(self):
        if self.code is None or self.message is None:
            raise productstatus.check.exceptions.EmptyCheckResultException('Empty check result')
        return (self.code, self.message,)

    def ok(self, *args, **kwargs):
        return self.set_result(OK, *args, **kwargs)

    def warning(self, *args, **kwargs):
        return self.set_result(WARNING, *args, **kwargs)

    def critical(self, *args, **kwargs):
        return self.set_result(CRITICAL, *args, **kwargs)

    def unknown(self, *args, **kwargs):
        return self.set_result(UNKNOWN, *args, **kwargs)
