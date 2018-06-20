Changelog
=========

v0.8
----

New
~~~

- Support file-based scheduler configuration. [Ash Wilson]

  Introduced file-based configuration for the scheduler.
  Configuration files are in 'ini' format. An
  example configuration file is named 'example.conf',
  and is located in the root of this repository.

  Removed the instance variables which are related to
  environment variables from Containerized()
  class. These variables will now be set when
  each container is run, based on the env_expand
  argument which has been introduced into the generic
  method for launching containers.

  Refactored firewall graph generator and ec2 footprint
  reporter functions into donbot project, which now will
  use the generic container launch functionality to
  perform these functions.

  Introduced Utility.log_stdout and Utility.log_stderr to
  consolidate log message printing.

  Celery version updated to 4.2.0rc4, to avoid issues with
  included pyamqp library in celery version 4.1.

  Closes #21

  Closes #23

  Closes #26

- Supports HALO_API_HOSTNAME environment variable. [Ash Wilson]

  This enables the use of halocelery against non-MTG grid instances.

  Closes #25

Changes
~~~~~~~

- Use travis-ci for testing. [Ash Wilson]

  Set up travis-ci for integration testing with Halo.

  Re-factor in halo.py for better performance, reliability, consistency.

  Re-factor in containerized.py for reduced duplication, created a generic
  container launch method for simplifying the process of adding newer
  functionality.

  Changed behavior of get_id_for_server_target() and
  get_id_for_group_target() to return a consistent format.
  Re-worked dependent functions to accommodate new
  functionality.

v0.7.0 (2018-05-07)
-------------------

- Rev halocelery to 0.7.0. [Jye Lee]

- Proxy https_proxy. [Jye Lee]

v0.6.0 (2018-04-02)
-------------------

- Rev to 0.6.0. [Jye Lee]

- Donbot/issue/27 report active issues for servers. [Jye Lee]

- Donbot/issue/30 add server counts to formatter. [Jye Lee]

- Donbot/issue/29 report group issues. [Jye Lee]

v0.5.0 (2018-03-27)
-------------------

- Test maintenance: rev to v0.5.0. [Jye Lee]

- Read mem limit as an env. [Jye Lee]

v0.4.9 (2018-03-20)
-------------------

- Fixed module import for tests. [Hana Lee]

- Fixed merge conflicts. [mong2]

- Updated version to v0.4.9. [Hana Lee]

- Added unit and functional tests. [Hana Lee]

- Added style - flake8 test. [Hana Lee]

- Added get_server_by_cve to search for servers by CVE ID. [Hana Lee]

- Added style - flake8 test. [Hana Lee]

v0.4.8 (2018-03-15)
-------------------

- Added group_path in group_facts and server_facts. changed the logic
  for get_id_for_group_target and get_id_for_server_target. [Hana Lee]

v0.4.7 (2018-01-09)
-------------------

- Add dockerfile. [Hana Lee]

v0.3 (2017-12-14)
-----------------

Changes
~~~~~~~

- Added Halo-EC2 footprint delta reporter. [Ash Wilson]

v0.1 (2017-08-04)
-----------------

New
~~~

- Quarantine and IP blocker functionality added. [Ash Wilson]

- Task report_group_firewall(group_name) returns a directed graph
  representation of the named group's firewall, in base64-encoded png
  format. [Ash Wilson]

- Added the ability to specify the hour in which to run scans and events
  export, using environment variables EVENT_EXPORT_HOUR and
  SCAN_EXPORT_HOUR. [Ash Wilson]

- Added periodic tasks for events and scans exporters. [Ash Wilson]

- Adding job to ship scans to S3. [Ash Wilson]

- Initial commit. [Ash Wilson]

Changes
~~~~~~~

- IP Blocker can un-block IPs. [Ash Wilson]

- Added minute setting for scheduled jobs. [Ash Wilson]

- Changing exec times for scheduled jobs. [Ash Wilson]

- Added events_to_s3() task. [Ash Wilson]

- Improved logging from scans_to_s3() task. [Ash Wilson]

- Adding a cleanup contingency routine for scans_to_s3().  You know.
  Just in case. [Ash Wilson]

- Fixed failed coercion issue in group policy formatting. [Ash Wilson]

- Get_events_by_server() will go back as far as a week to find events.
  [Ash Wilson]

- Changed default number of events in query to 5 most recent. [Ash
  Wilson]

  chg: dev: Improved logging for server reports

- Improve consistency in formatting output for chatbot. [Ash Wilson]

Fix
~~~

- Corrected issues with imports. [Ash Wilson]


