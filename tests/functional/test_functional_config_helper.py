from celery.schedules import crontab
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


class TestIntegrationConfigManager:
    def build_config_manager_object(self):
        """Return a ConfigManager object."""
        c_manager = apputils.ConfigManager(fixture_dir)
        return c_manager

    def get_config_from_file(self, file_name):
        """Return a dict representing config from file in fixtures dir."""
        file_path = os.path.join(fixture_dir, file_name)
        conf = apputils.ConfigManager.get_scheduled_task_config_from_file(file_path)  # NOQA
        return conf._sections

    def test_config_manager_multiple_files(self):
        """Ensure that we're consuming multiple files from the config dir."""
        c_manager = self.build_config_manager_object()
        assert len(c_manager.scheduled_tasks.items()) == 2

    def test_override_task_config(self):
        """Ensure that task configs are overridden by same-named tasks."""
        c_manager = self.build_config_manager_object()
        tasks = c_manager.scheduled_tasks
        assert tasks["hello_world"]["log_config"]["task_started"] == "OVERRIDE"

    def test_build_beat_config(self):
        """Ensure that we can build beat configs."""
        c_manager = self.build_config_manager_object()
        assert c_manager.beat_tasks_from_config()

    def test_preserve_var_case(self):
        """Ensure that case is preserved for keys."""
        config_manager = apputils.ConfigManager
        c_file = os.path.join(fixture_dir, 'sample_config_1.conf')
        conf = config_manager.get_scheduled_task_config_from_file(c_file)._sections  # NOQA
        assert "ARG_1" in conf["env_literal"]

    def test_build_beat_task(self):
        """Build and validate a beat task."""
        expected_sections = ["task", "schedule", "args"]
        conf_dict = self.get_config_from_file("sample_config_1.conf")
        conf_dict["task_config"]["read_only"] = True
        beat_conf = apputils.ConfigManager.build_beat_task(conf_dict)
        # Top-level keys check
        assert not [x for x in expected_sections if x not in beat_conf]
        args_expected = ("docker.io/halotools/notifyuser:v1",
                         {"ARG_1": "VAL_1"},
                         {"API_KEY_1": "API_VAL_1"},
                         "5",
                         {"task_started": "Doing the thing now",
                          "task_finished": "Done doing the thing now",
                          "task_retried": "Try doing the thing again now",
                          "task_failed": "Failed to do the thing"},
                         True)
        cron_expected = crontab(hour="*",
                                minute="*",
                                day_of_week="*",
                                day_of_month="*",
                                month_of_year="*")
        assert args_expected == beat_conf["args"]
        assert cron_expected == beat_conf["schedule"]
