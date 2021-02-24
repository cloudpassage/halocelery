"""Configuration Manager."""
from celery.schedules import crontab
from .config_validator import ConfigValidator
from .utility import Utility
from string import Template
import configparser
import os


class ConfigManager(object):
    sections_required = ["task_config", "log_config", "schedule",
                         "env_literal", "env_expand"]
    task_config_required = ['task_name', 'image', 'retry', 'read_only']
    log_config_required = ['task_started', 'task_finished',
                           'task_retried', 'task_failed']
    schedule_required = ['minute', 'hour', 'day_of_week',
                         'day_of_month', 'month_of_year']

    def __init__(self, config_path):
        self.scheduled_tasks = self.load_config_files(config_path)
        if len(self.scheduled_tasks) > 0:
            self.print_tasks(self.scheduled_tasks)

    def load_config_files(self, config_path):
        """Load all valid config files from path, print task config to stdout.

        Args:
            config_path(str): Path to configuration directory.

        """
        scheduled_tasks = {}
        config_files = self.get_config_files(config_path)
        for target in sorted(config_files):
            msg = "ConfigManager: Parsing config file: %s" % target
            Utility.log_stdout(msg)
            config = self.get_scheduled_task_config_from_file(target)
            if not ConfigValidator.config_is_qualified(config):
                msg = "ConfigManager: %s is not a scheduler config." % target
                Utility.log_stdout(msg)
                continue
            err_msg = ConfigValidator.validate_config(config)
            if err_msg == "":
                config_dict = config._sections
                task_name = config_dict["task_config"]["task_name"]
                scheduled_tasks[task_name] = config_dict
                scheduled_tasks[task_name]["task_config"]["read_only"] = (
                    config.getboolean("task_config", "read_only"))
        return scheduled_tasks

    def beat_tasks_from_config(self):
        """Return dictionary that describes celerybeat tasks, from config."""
        beats = {}
        for task_name, conf in self.scheduled_tasks.items():
            beats[task_name] = self.build_beat_task(conf)
        return beats

    @classmethod
    def build_beat_task(cls, conf):
        """Return beat task, built from conf.

        Args:
            conf(dict): Configuration parsed from file.
        Returns:
            dict: Dictionary describing a scheduled task.
        """
        # We remove the __name__ keys that ConfigParser injects.
        conf["env_literal"].pop("__name__")
        conf["env_expand"].pop("__name__")
        conf["log_config"].pop("__name__")
        beat = {
            'task': 'halocelery.tasks.generic_bound_containerized_task',
            'schedule': crontab(
                hour=conf["schedule"]["hour"],
                minute=conf["schedule"]["minute"],
                day_of_week=conf["schedule"]["day_of_week"],
                day_of_month=conf["schedule"]["day_of_month"],
                month_of_year=conf["schedule"]["month_of_year"]),
            'args': (conf["task_config"]["image"],
                     conf["env_literal"],
                     conf["env_expand"],
                     conf["task_config"]["retry"],
                     conf["log_config"],
                     conf["task_config"]["read_only"])}
        return beat

    @classmethod
    def format_task(cls, task):
        """Format task config into printable text."""
        s_sched = "Schedule:\n"
        s_sched += "\tMinute: $minute\n"
        s_sched += "\tHour: $hour\n"
        s_sched += "\tDay of week: $day_of_week\n"
        s_sched += "\tDay of month: $day_of_month\n"
        s_sched += "\tMonth of year: $month_of_year\n"
        s_task = "Task: $task_name\nContainer image: $image\nRetries: $retry\n"
        task_text = Template(s_task).safe_substitute(task["task_config"])
        task_text += Template(s_sched).safe_substitute(task["schedule"])
        return task_text

    @classmethod
    def get_config_files(cls, config_path):
        """Return a list of .conf files in config_path."""
        conf_files = [os.path.join(config_path, f)
                      for f in os.listdir(config_path)
                      if os.path.isfile(os.path.join(config_path, f))
                      and f.endswith(".conf")]
        return conf_files

    @classmethod
    def get_scheduled_task_config_from_file(cls, config_file_path):
        """Get scheduled task config from file.

        Args:
            config_file_path(str): Path to config file.

        Returns:
            config: RawConfigParser() instance.

        """
        config = configparser.RawConfigParser({}, dict)
        config.optionxform = str
        with open(config_file_path, 'r') as conf_file:
            config.readfp(conf_file)
        return config

    @classmethod
    def print_tasks(cls, tasks):
        """Print task config to stdout, for logging and troubleshooting."""
        result = "Scheduled tasks:\n"
        result += "\n==\n".join([cls.format_task(j[1]) for j in tasks.items()])
        Utility.log_stdout(result)
