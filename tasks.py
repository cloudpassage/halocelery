from __future__ import absolute_import, unicode_literals
from .celery import app
from . import apputils
import os


@app.task
def list_all_groups_formatted():
    halo = apputils.Halo()
    return halo.list_all_groups_formatted()


@app.task
def list_all_servers_formatted():
    halo = apputils.Halo()
    return halo.list_all_servers_formatted()


@app.task
def report_group_formatted(target):
    halo = apputils.Halo()
    return halo.generate_group_report_formatted(target)


@app.task
def report_server_formatted(target):
    """Accepts a hostname or server_id"""
    halo = apputils.Halo()
    return halo.generate_server_report_formatted(target)


@app.task
def servers_in_group_formatted(target):
    """Accepts groupname or ID"""
    # !!! TODO: Need to print the group name at the top of the output!
    halo = apputils.Halo()
    return halo.list_servers_in_group_formatted(target)


@app.task
def search_server_by_cve(target):
    halo = apputils.Halo()
    return halo.get_server_by_cve(target)


@app.task
def quarantine_server(server_id, quarantine_group_name):
    halo = apputils.Halo()
    quarantine_group_id = halo.get_id_for_group_target(quarantine_group_name)
    halo.move_server(server_id, quarantine_group_id)
    msg = ("Quarantined server %s in group %s\n" % (server_id,
                                                    quarantine_group_name))
    return msg


@app.task
def add_ip_to_list(ip_address, ip_zone_name):
    halo = apputils.Halo()
    return halo.add_ip_to_zone(ip_address, ip_zone_name)


@app.task
def remove_ip_from_list(ip_address, ip_zone_name):
    halo = apputils.Halo()
    return halo.remove_ip_from_zone(ip_address, ip_zone_name)


@app.task
def generic_containerized_task(image, env_literal, env_expand,
                               read_only=False):
    """Wrap Containerized.generic_container_launch_attached() for ad-hoc tasks.

    This task is a generic interface for a service to launch a container and
    collect the resulting output from the container's STDOUT.

    Args:
        image(str): Container image to launch.
        env_literal(dict): Dictionary containing environment variables to be
            passed into the container launch configuration, unmodified.
        env_expand(dict): Dictionary containing arguments to be expanded
            from environment variables, then added to the environment variables
            defined in env_literal.  The value for every key in the dictionary
            is replaced by the corresponding environment variable.  For
            instance, with this dictionary: ``{'API': 'API_KEY'}``, and
            the existence of an environment variable ``API_KEY`` set to
            ``abc123``, before launching the container, the dictionary will be
            processed and the result will be ``{'API': 'abc123'}``.  The result
            will be added to the environment variables used to launch the
            container.
        retry(int): Number of times to retry after failure.
        log_messages(dict): This contains the log messages used to indicate
            the activities and success or failure of the task.  Expected keys
            in this dictionary include ``task_started``, ``task_finished``,
            ``task_retried``, and ``task_failed``.
        read_only(bool): Run the container with a read-only filesystem.
            Defaults to False.

    Returns:
        (str): Returns STDOUT from the container.
    """
    container = apputils.Containerized()
    return container.generic_container_launch_attached(image,
                                                       env_literal.copy(),
                                                       env_expand.copy(),
                                                       read_only)


@app.task(bind=True)
def generic_bound_containerized_task(self, image, env_literal, env_expand,
                                     retry, log_messages, read_only=False):
    """Wrap Containerized.generic_container_launch_attached() for scheduler.

    This task is a generic interface for scheduled tasks to launch containers.

    Args:
        image(str): Container image to launch.
        env_literal(dict): Dictionary containing environment variables to be
            passed into the container launch configuration, unmodified.
        env_expand(dict): Dictionary containing arguments to be expanded
            from environment variables, then added to the environment variables
            defined in env_literal.  The value for every key in the dictionary
            is replaced by the corresponding environment variable.  For
            instance, with this dictionary: ``{'API': 'API_KEY'}``, and
            the existence of an environment variable ``API_KEY`` set to
            ``abc123``, before launching the container, the dictionary will be
            processed and the result will be ``{'API': 'abc123'}``.  The result
            will be added to the environment variables used to launch the
            container.
        retry(int): Number of times to retry after failure.
        log_messages(dict): This contains the log messages used to indicate
            the activities and success or failure of the task.  Expected keys
            in this dictionary include ``task_started``, ``task_finished``,
            ``task_retried``, and ``task_failed``.
    """
    start_msg = log_messages["task_started"]
    finished_msg = log_messages["task_finished"]
    retried_msg = log_messages["task_retried"]
    fail_msg = log_messages["task_failed"]
    container = apputils.Containerized()
    try:
        apputils.Utility.log_stdout("TaskRunner: %s" % start_msg)
        container.generic_container_launch_attached(image, env_literal.copy(),
                                                    env_expand.copy(),
                                                    read_only)
        apputils.Utility.log_stdout("TaskRunner: %s" % finished_msg)
    except Exception as e:
        apputils.Utility.log_stderr("TaskRunner: %s" % fail_msg)
        apputils.Utility.log_stderr("TaskRunner Exception: %s" % e)
        retries = self.request.retries
        if retries >= retry:
            apputils.Utility.log_stderr("TaskRunner Retry %s: %s" % (retries,
                                                                     retried_msg))  # NOQA
        else:
            apputils.Utility.log_stderr("TaskRunner Failure: %s" % fail_msg)
        raise self.retry(countdown=120, exc=e, max_retries=retry)


config_manager = apputils.ConfigManager(os.getenv("HALOCELERY_CONFIG_DIR",
                                        "/app/halocelery/config/"))

'''config_manager = apputils.ConfigManager(os.getenv("HALOCELERY_CONFIG_DIR",
                                        "/halocelery/config/"))'''

app.conf.beat_schedule = config_manager.beat_tasks_from_config()
