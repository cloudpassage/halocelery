from __future__ import print_function
import datetime
import re
import sys


class Utility(object):
    """This is a collection of widely-used functions"""

    @classmethod
    def date_to_iso8601(cls, date_obj):
        """Returns an ISO8601-formatted string for datetime arg"""
        retval = date_obj.isoformat()
        return retval

    @classmethod
    def event_is_critical(cls, event):
        return event["critical"]

    @classmethod
    def ipaddress_list_from_string(cls, string_of_ips):
        ip_list = string_of_ips.split(',')
        return ip_list

    @classmethod
    def ipaddress_string_from_list(cls, list_structure):
        ip_str = ",".join(list_structure)
        return ip_str

    @classmethod
    def iso8601_arbitrary_days_ago(cls, days_ago):
        return Utility.date_to_iso8601(datetime.date.today() -
                                       datetime.timedelta(days=days_ago))

    @classmethod
    def iso8601_now(cls):
        return Utility.date_to_iso8601(datetime.datetime.utcnow())

    @classmethod
    def iso8601_today(cls):
        return Utility.date_to_iso8601(datetime.date.today())

    @classmethod
    def iso8601_yesterday(cls):
        return Utility.iso8601_arbitrary_days_ago(1)

    @classmethod
    def iso8601_one_week_ago(cls):
        return Utility.iso8601_arbitrary_days_ago(7)

    @classmethod
    def iso8601_one_month_ago(cls):
        """In this case, we assume 30 days"""
        return Utility.iso8601_arbitrary_days_ago(30)

    @classmethod
    def log_stdout(cls, message, component="Halocelery"):
        """Log messages to stdout.

        Args:
            message(str): Message to be logged to stdout.
            component(str): Component name. Defaults to "Halocelery".
        """
        out = "%s: %s" % (component, message)
        print(out, file=sys.stdout)
        return

    @classmethod
    def log_stderr(cls, message, component="Halocelery"):
        """Log messages to stderr.

        Args:
            message(str): Message to be logged to stdout.
            component(str): Component name. Defaults to "Halocelery".
        """
        out = "%s: %s" % (component, message)
        print(out, file=sys.stderr)
        return

    @classmethod
    def target_date_is_valid(cls, start_date):
        """ Tests date stamp for validity """
        d_rgex = r'^(19|20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01])$'
        canary = re.compile(d_rgex)
        if canary.match(start_date):
            return True
        else:
            return False
