from __future__ import absolute_import, unicode_literals
from .celery import app
import halocelery.apputils as apputils


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
    return halo.list_servers_in_group_formatted(target)
