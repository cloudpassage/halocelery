"""Validator for config files."""
import configparser


class ConfigValidator(object):
    sections_required = ["task_config", "log_config", "schedule",
                         "env_literal", "env_expand"]
    task_config_required = ['task_name', 'image', 'retry', 'read_only']
    log_config_required = ['task_started', 'task_finished',
                           'task_retried', 'task_failed']
    schedule_required = ['minute', 'hour', 'day_of_week',
                         'day_of_month', 'month_of_year']

    @classmethod
    def config_is_qualified(cls, config):
        """Config is qualified if [service] section has 'module = scheduler'.

        Args:
            config(RawConfigParser): Configuration object to be qualified.

        Returns:
            bool: True if qualified, False otherwise.
        """
        try:
            if config.get("service", "module") == "scheduler":
                return True
        except (configparser.NoSectionError, configparser.NoOptionError):
            pass
        return False

    @classmethod
    def validate_config(cls, config):
        """Wrap all config validation operations.

        Args:
            config(RawConfigParser): Instance of RawConfigParser.

        Returns:
            str: An empty string indicates that the config is valid. Otherwise,
                a string containing validation failure information will be
                returned.
        """
        section_requirements = [("task_config", cls.task_config_required),
                                ("log_config", cls.log_config_required),
                                ("schedule", cls.schedule_required)]
        err_msg = ""
        err_msg += cls.validate_section_presence(config, cls.sections_required)
        for section in section_requirements:
            section_name = section[0]
            section_fields = section[1]
            err_msg += cls.validate_section_keys(config, section_name,
                                                 section_fields)
        return err_msg

    @classmethod
    def validate_section_keys(cls, config, section_name, section_fields):
        """Return empty string if all required fields are presentself.

        If any fields are missing, a string describing the missing fields
        will be returned.

        If the section is missing, the string returned will list the section's
        required fields.

        Args:
            config(RawConfigParser): Instance of RawConfigParser.
            section_name(str): Name of section to inspect.
            section_fields(list): List of required fields for section.
        """
        err_msg = ""
        if not config.has_section(section_name):
            err_msg += ("ConfigValidator: [%s] section requires %s\n" %
                        (section_name, ", ".join(section_fields)))
            return err_msg
        missing_keys = [x for x in section_fields
                        if x not in config.options(section_name)]
        if missing_keys:
            err_msg += ("ConfigValidator: Mising from [%s] section: %s\n"
                        % (section_name, ", ".join(missing_keys)))
        return err_msg

    @classmethod
    def validate_section_presence(cls, config, sections_required):
        """Return an empty string if all required sections are present.

        If any sections are missing from the config, the returned string will
        indicate what sections are missing in a log message.
        """
        err_msg = ""
        missing_sections = [x for x in sections_required
                            if x not in config.sections()]
        if missing_sections:
            err_msg += ("ConfigValidator: Missing sections in config: %s\n" %
                        ", ".join(missing_sections))
        return err_msg
