from __future__ import absolute_import, unicode_literals
from .celery import app
import halocelery.apputils as apputils
from celery.schedules import crontab
import tempfile
import os


events_hour = int(os.getenv("EVENT_EXPORT_HOUR", 21))
events_min = int(os.getenv("EVENT_EXPORT_MIN", 01))
scans_hour = int(os.getenv("SCAN_EXPORT_HOUR", 21))
scans_min = int(os.getenv("SCAN_EXPORT_MIN", 01))


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
def report_group_firewall(target):
    """Accepts a hostname or server_id"""
    halo = apputils.Halo()
    return halo.generate_group_firewall_report(target)


@app.task
def report_server_scan_graph(target):
    """Accepts server name or ID, returns a base64-encoded png"""
    halo = apputils.Halo()
    return halo.generate_scan_compliance_graph_for_server(target)

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
    ip_zone_id = halo.get_id_for_ip_zone(ip_zone_name)
    if ip_zone_id is None:
        msg = ("Unable to determine ID for IP zone %s!!\n" % ip_zone_name)
        return msg
    return halo.add_ip_to_zone(ip_address, ip_zone_id)

@app.task(bind=True)
def scans_to_s3(self, target_date, s3_bucket_name):
    output_dir = tempfile.mkdtemp()
    halo = apputils.Halo()
    try:
        halo.scans_to_s3(target_date, s3_bucket_name, output_dir)
    except Exception as e:
        "Exception encountered: %s" % e
        "Cleaning up temp dir %s" % output_dir
        raise self.retry(countdown=120, exc=e, max_retries=5)


@app.task(bind=True)
def events_to_s3(self, target_date, s3_bucket_name):
    output_dir = tempfile.mkdtemp()
    halo = apputils.Halo()
    try:
        halo.events_to_s3(target_date, s3_bucket_name, output_dir)
    except Exception as e:
        "Exception encountered: %s" % e
        "Cleaning up temp dir %s" % output_dir
        raise self.retry(countdown=120, exc=e, max_retries=5)


app.conf.beat_schedule = {
    'daily-events-export': {
        'task': 'halocelery.tasks.events_to_s3',
        'schedule': crontab(hour=events_hour, minute=events_min),
        'args': (apputils.Utility.iso8601_yesterday(),
                 os.getenv("EVENTS_S3_BUCKET"))},
    'daily-scans-export': {
        'task': 'halocelery.tasks.scans_to_s3',
        'schedule': crontab(hour=scans_hour, minute=scans_min),
        'args': (apputils.Utility.iso8601_yesterday(),
                 os.getenv("SCANS_S3_BUCKET"))}
    }
