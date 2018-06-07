import imp
import os
import sys


module_name = 'apputils'
here_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(here_dir, '../../')
sys.path.append(module_path)
fp, pathname, description = imp.find_module(module_name)
apputils = imp.load_module(module_name, fp, pathname, description)

fixture_dir = os.path.join(here_dir, '../fixtures')


class TestUnitConfigValidator:
    def get_config_object_from_file(self, file_path):
        """This will pass the basic config qualifier."""
        conf = apputils.ConfigManager.get_scheduled_task_config_from_file(file_path)  # NOQA
        return conf

    def test_config_validator_no_missing_sections(self):
        """This passes; all required sections present."""
        conf_file = os.path.join(fixture_dir, "sample_config_1.conf")
        conf = self.get_config_object_from_file(conf_file)
        required = ["service", "task_config"]
        res = apputils.ConfigValidator.validate_section_presence(conf,
                                                                 required)
        assert res == ""

    def test_config_validator_missing_sections(self):
        """This fails. Missing section \"two\""""
        conf_file = os.path.join(fixture_dir, "sample_config_1.conf")
        conf = self.get_config_object_from_file(conf_file)
        required = ["two"]
        res = apputils.ConfigValidator.validate_section_presence(conf,
                                                                 required)
        assert res != ""

    def test_config_validator_no_missing_fields(self):
        """This passes. No missing fields."""
        conf_file = os.path.join(fixture_dir, "sample_config_1.conf")
        conf = self.get_config_object_from_file(conf_file)
        section = "service"
        required = ["module"]
        res = apputils.ConfigValidator.validate_section_keys(conf, section,
                                                             required)
        assert res == ""

    def test_config_validator_missing_fields(self):
        """This test fails because we don't have \"two\" in \"service\"."""
        conf_file = os.path.join(fixture_dir, "sample_config_1.conf")
        conf = self.get_config_object_from_file(conf_file)
        section = "service"
        required = ["two"]
        res = apputils.ConfigValidator.validate_section_keys(conf, section,
                                                             required)
        assert res != ""

    def test_validate_config_good(self):
        """Good config returns empty string."""
        conf_file = os.path.join(fixture_dir, "sample_config_1.conf")
        conf = self.get_config_object_from_file(conf_file)
        res = apputils.ConfigValidator.validate_config(conf)
        assert res == ""

    def test_validate_config_bad(self):
        """Bad config returns non-empty string."""
        conf_file = os.path.join(fixture_dir, "sample_config_7.conf")
        conf = self.get_config_object_from_file(conf_file)
        res = apputils.ConfigValidator.validate_config(conf)
        assert res != ""
