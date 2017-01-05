from __future__ import absolute_import, unicode_literals
from .celery import app
import halocelery.apputils


@app.task
def list_all_groups():
    halo = apputils.Halo()
    return halo.list_all_groups()


@app.task
def list_all_servers():
    halo = apputils.Halo()
    return halo.list_all_servers()


@app.task
def report_group(target):
    halo = apputils.Halo()
    return halo.generate_group_report(target)


@app.task
def report_server(target):
    """Accepts a hostname or server_id"""
    halo = apputils.Halo()
    return halo.generate_server_report(target)


@app.task
def servers_in_group(target):
    """Accepts groupname or ID"""
    return halo.list_servers_in_group(target)
