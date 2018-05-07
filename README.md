# Halo tasks for Celery

The code in this repository is typically used to implement an asynchronous task dispatcher for donbot (https://github.com/cloudpassage/don-bot).

This is how the halocelery codebase is organized:

* `tasks.py`: This is where all celery tasks are defined.  This is imported in donbot's app/runner.py file.
* `apputils`: This library contains a collection of functionality that supports the tasks defined in `tasks.py`
    * `containerized.py`: This contains the supporting functionality for running containerized tasks.
    * `formatter.py`: This is used for formatting task output for better representation in Slack (via donbot).
    * `halo.py`: Functionality in this file supports interacting with the CloudPassage Halo API.
    * `utility.py`: This is a general collection of utility functions, none of which can be exclusively classified under the other functionality classes.
