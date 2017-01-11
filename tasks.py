from __future__ import absolute_import, unicode_literals
from .celery import app
import halocelery.apputils as apputils

import scanslib
import tempfile

import cloudpassage

import os
import time
from datetime import datetime


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
def scans_to_s3(target_date, s3_bucket_name):
    config = cloudpassage.ApiKeyManager()
    env_date = target_date
    output_dir = tempfile.mkdtemp()
    print("Using temp dir: %s" % output_dir)
    scans_per_file = 10000
    start_time = datetime.now()
    s3_bucket_name = s3_bucket_name
    file_number = 0
    counter = 0
    # Validate date
    if scanslib.Utility.target_date_is_valid(env_date) is False:
        msg = "Bad date! %s" % env_date
        sys.exit(2)
    scan_cache = scanslib.GetScans(config.key_id, config.secret_key,
                                   scans_per_file, env_date)
    for batch in scan_cache:
        counter = counter + len(batch)
        try:
            print("Last timestamp in batch: %s" % batch[-1]["created_at"])
        except IndexError:
            pass
        file_number = file_number + 1
        output_file = "Halo-Scans_%s_%s" % (env_date, str(file_number))
        full_output_path = os.path.join(output_dir, output_file)
        # print("Writing %s" % full_output_path)
        dump_file = scanslib.Outfile(full_output_path)
        dump_file.flush(batch)
        dump_file.compress()
        if s3_bucket_name is not None:
            time.sleep(1)
            dump_file.upload_to_s3(s3_bucket_name)
    # Cleanup and print results
    print("Deleting temp dir: %s" % output_dir)
    shutil.rmtree(output_dir)
    end_time = datetime.now()

    difftime = str(end_time - start_time)

    print("Total time taken to download %s scans for %s: %s") % (str(counter),
                                                                 env_date,
                                                                 difftime)
