import datetime
import os
import sys
import imp

module_name = 'apputils'
here_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(here_dir, '../../')
sys.path.append(module_path)
fp, pathname, description = imp.find_module(module_name)
apputils = imp.load_module(module_name, fp, pathname, description)


class TestUnitUtility:
    def test_instantiation(self):
        assert apputils.Utility()

    def test_date_to_iso8601(self):
        utility = apputils.Utility()
        date = datetime.date(2008, 3, 12)
        iso_date = utility.date_to_iso8601(date)
        assert iso_date == '2008-03-12'

    def test_event_is_critical(self):
        data = {"critical": True}
        utility = apputils.Utility()
        assert utility.event_is_critical(data)

    def test_target_date_is_invalid(self):
        utility = apputils.Utility()
        assert not utility.target_date_is_valid('2020-22-12')

    def test_target_date_is_valid(self):
        utility = apputils.Utility()
        assert utility.target_date_is_valid('2020-02-12')

    def test_ipaddress_string_from_list(self):
        utility = apputils.Utility()
        data = ["123", "456"]
        ip_string = utility.ipaddress_string_from_list(data)
        assert ip_string == "123,456"

    def test_ipaddress_list_from_string(self):
        utility = apputils.Utility()
        data = "123,456"
        ip_list = utility.ipaddress_list_from_string(data)
        assert ip_list == ["123", "456"]
