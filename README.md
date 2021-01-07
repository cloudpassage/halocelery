# Halo tasks for Celery

The code in this repository is typically used to implement an asynchronous task dispatcher for donbot (https://github.com/cloudpassage/don-bot).

This is how the halocelery codebase is organized:

* `tasks.py`: This is where all celery tasks are defined.  This is imported by
the microservices that initiate tasks via celery.
* `apputils`: This library contains a collection of functionality that supports the tasks defined in `tasks.py`
    * 'config_manager.py': This is responsible for consuming config files and
    producing the configuration settings used by the task scheduler.
    * `config_validator.py`: This validates configuration file content.
    * `containerized.py`: This contains the supporting functionality for
    running containerized tasks. Container output is returned in the form of
    a base64-encoded string.
    * `formatter.py`: This is used for formatting task output for better
    representation in Slack (via donbot).
    * `halo.py`: Functionality in this file supports interacting with the
    CloudPassage Halo API.
    * `utility.py`: This is a general collection of utility functions, none of
    which can be exclusively classified under the other functionality classes.

Notes:

* Configuration files for the scheduler are in the `INI` format. A sample
configuration file can be found [here](./example.conf)
* The config manager expects, at the minimum, the following sections defined in
each config file: `[service]`, `[task_config]`, `[log_config]`, `[schedule]`,
`[env_literal]`, and `[env_expand]`.  These sections are described in detail,
in the sample configuration file referenced above.

<!---
#CPTAGS:community-supported automation
#TBICON:images/python_icon.png
-->
