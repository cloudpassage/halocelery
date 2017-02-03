import base64
import cloudpassage
from datetime import datetime
import os
import shutil
import time
from get_scans import GetScans
from get_events import GetEvents
from outfile import Outfile
from utility import Utility as util
from formatter import Formatter as fmt
from firewallgraph import FirewallGraph


class Halo(object):
    def __init__(self):
        self.halo_api_key = os.getenv("HALO_API_KEY")
        self.halo_api_secret = os.getenv("HALO_API_SECRET_KEY")
        self.session = cloudpassage.HaloSession(self.halo_api_key,
                                                self.halo_api_secret)

    def list_all_servers_formatted(self):
        servers = cloudpassage.Server(self.session)
        return fmt.format_list(servers.list_all(), "server_facts")

    def list_all_groups_formatted(self):
        groups = cloudpassage.ServerGroup(self.session)
        return fmt.format_list(groups.list_all(), "group_facts")

    def generate_server_report_formatted(self, target):
        server_id = self.get_id_for_server_target(target)
        result = ""
        if server_id is not None:
            print("ServerReport: Starting report for %s" % server_id)
            server_obj = cloudpassage.Server(self.session)
            print("ServerReport: Getting server facts")
            result = fmt.format_item(server_obj.describe(server_id),
                                     "server_facts")
            print("ServerReport: Getting server issues")
            result += fmt.format_list(self.get_issues_by_server(server_id),
                                      "issue")
            print("ServerReport: Getting server events")
            result += fmt.format_list(self.get_events_by_server(server_id),
                                      "event")
        return result

    def generate_group_report_formatted(self, target):
        group_id = self.get_id_for_group_target(target)
        result = ""
        if group_id is not None:
            group_obj = cloudpassage.ServerGroup(self.session)
            grp_struct = group_obj.describe(group_id)
            result = fmt.format_item(grp_struct, "group_facts")
            result += self.get_group_policies(grp_struct)
        return result

    def get_group_policies(self, grp_struct):
        retval = ""
        firewall_keys = ["firewall_policy_id", "windows_firewall_policy_id"]
        csm_keys = ["policy_ids", "windows_policy_ids"]
        fim_keys = ["fim_policy_ids", "windows_fim_policy_ids"]
        lids_keys = ["lids_policy_ids"]
        print("Getting meta for FW policies")
        for fwp in firewall_keys:
            retval += self.get_policy_metadata(grp_struct[fwp], "FW")
        print("Getting meta for CSM policies")
        for csm in csm_keys:
            retval += self.get_policy_list(grp_struct[csm], "CSM")
        print("Getting meta for FIM policies")
        for fim in fim_keys:
            retval += self.get_policy_list(grp_struct[fim], "FIM")
        print("Getting meta for LIDS policies")
        for lids in lids_keys:
            retval += self.get_policy_list(grp_struct[lids], "LIDS")
        print("Gathered all policy metadata successfully")
        return retval

    def get_policy_list(self, policy_ids, policy_type):
        retval = ""
        for policy_id in policy_ids:
            retval += self.get_policy_metadata(policy_id, policy_type)
        return retval

    def get_policy_metadata(self, policy_id, policy_type):
        p_ref = {"FW": " Firewall",
                 "CSM": "Configuration",
                 "FIM": "File Integrity Monitoring",
                 "LIDS": "Log-Based IDS"}
        if policy_id is None:
            return ""
        elif policy_type == "FIM":
            pol = cloudpassage.FimPolicy(self.session)
        elif policy_type == "CSM":
            pol = cloudpassage.ConfigurationPolicy(self.session)
        elif policy_type == "FW":
            pol = cloudpassage.FirewallPolicy(self.session)
        elif policy_type == "LIDS":
            pol = cloudpassage.LidsPolicy(self.session)
        else:
            return ""
        retval = fmt.policy_meta(pol.describe(policy_id), p_ref[policy_type])
        return retval

    def get_id_for_group_target(self, target):
        """Attempts to get group_id using arg:target as group_name, then id"""
        group = cloudpassage.ServerGroup(self.session)
        orig_result = group.list_all()
        result = []
        for x in orig_result:
            if x["name"] == target:
                result.append(x)
        if len(result) > 0:
            return result[0]["id"]
        else:
            try:
                result = group.describe(target)["id"]
            except cloudpassage.CloudPassageResourceExistence:
                result = None
            except KeyError:
                result = None
        return result

    def get_id_for_server_target(self, target):
        """Attempts to get server_id using arg:target as hostname, then id"""
        server = cloudpassage.Server(self.session)
        result = server.list_all(hostname=target)
        if len(result) > 0:
            return result[0]["id"]
        else:
            try:
                result = server.describe(target)["id"]
            except:
                print("Not a hostnamename or server ID: %s\n" % target)
                result = None
        return result

    def get_events_by_server(self, server_id, number_of_events=20):
        """Return events for a server, Goes back up to a week to find 20."""
        events = []
        h_h = cloudpassage.HttpHelper(self.session)
        starting = util.iso8601_one_week_ago()
        search_params = {"server_id": server_id,
                         "sort_by": "created_at.desc",
                         "since": starting}
        halo_events = h_h.get("/v1/events", params=search_params)["events"]
        for event in halo_events:
            if len(events) >= number_of_events:
                return events
            events.append(event)
        return events

    def get_issues_by_server(self, server_id):
        pagination_key = 'issues'
        url = '/v2/issues'
        params = {'agent_id': server_id}
        hh = cloudpassage.HttpHelper(self.session)
        issues = hh.get_paginated(url, pagination_key, 5, params=params)
        return issues

    def list_servers_in_group_formatted(self, target):
        """Return a list of servers in group after sending through formatter"""
        group = cloudpassage.ServerGroup(self.session)
        group_id = self.get_id_for_group_target(target)
        if group_id is None:
            return group_id
        else:
            return fmt.format_list(group.list_members(group_id),
                                   "server_facts")

    def scans_to_s3(self, target_date, s3_bucket_name, output_dir):
        ret_msg = ""
        ret_msg += "Using temp dir: %s \n" % output_dir
        scans_per_file = 10000
        start_time = datetime.now()
        s3_bucket_name = s3_bucket_name
        file_number = 0
        counter = 0
        # Validate date
        if util.target_date_is_valid(target_date) is False:
            msg = "Bad date! %s" % target_date
            raise AttributeError(msg)
        scan_cache = GetScans(self.halo_api_key, self.halo_api_secret,
                              scans_per_file, target_date)
        for batch in scan_cache:
            counter = counter + len(batch)
            try:
                print("Last timestamp in batch: %s" % batch[-1]["created_at"])
            except IndexError:
                pass
            file_number = file_number + 1
            output_file = "Halo-Scans_%s_%s" % (target_date, str(file_number))
            full_output_path = os.path.join(output_dir, output_file)
            # print("Writing %s" % full_output_path)
            dump_file = Outfile(full_output_path)
            dump_file.flush(batch)
            dump_file.compress()
            if s3_bucket_name is not None:
                time.sleep(1)
                dump_file.upload_to_s3(s3_bucket_name)
        # Cleanup and print results
        ret_msg += "Deleting temp dir: %s" % output_dir
        shutil.rmtree(output_dir)
        end_time = datetime.now()

        difftime = str(end_time - start_time)

        ret_msg += "Total time taken: %s scans for %s: %s" % (str(counter),
                                                              target_date,
                                                              difftime)
        return ret_msg

    def generate_group_firewall_report(self, target):
        group_id = self.get_id_for_group_target(target)
        if group_id is None:
            retval = "Group not found: %s\n" % target
        else:
            retval = self.firewall_report_for_group_id(group_id)
        return retval

    def firewall_report_for_group_id(self, group_id):
        fw_obj = cloudpassage.FirewallPolicy(self.session)
        group_obj = cloudpassage.ServerGroup(self.session)
        group_struct = group_obj.describe(group_id)
        fw_polid = group_struct["linux_firewall_policy_id"]
        if fw_polid is None:
            retval = "No firewall policy for: %s\n" % target
        else:
            grapher = FirewallGraph(fw_obj.describe(fw_polid))
            retval = FirewallGraph.dot_to_png(grapher.make_dotfile())
        return retval

    def events_to_s3(self, target_date, s3_bucket_name, output_dir):
        ret_msg = ""
        ret_msg += "Using temp dir: %s \n" % output_dir
        events_per_file = 10000
        start_time = datetime.now()
        s3_bucket_name = s3_bucket_name
        file_number = 0
        counter = 0
        # Validate date
        if util.target_date_is_valid(target_date) is False:
            msg = "Bad date! %s" % target_date
            raise AttributeError(msg)
        event_cache = GetEvents(self.halo_api_key, self.halo_api_secret,
                                events_per_file, target_date)
        for batch in event_cache:
            counter = counter + len(batch)
            try:
                print("Last timestamp in batch: %s" % batch[-1]["created_at"])
            except IndexError:
                pass
            file_number = file_number + 1
            output_file = "Halo-Events_%s_%s" % (target_date, str(file_number))
            full_output_path = os.path.join(output_dir, output_file)
            dump_file = Outfile(full_output_path)
            dump_file.flush(batch)
            dump_file.compress()
            if s3_bucket_name is not None:
                time.sleep(1)
                dump_file.upload_to_s3(s3_bucket_name)
        # Cleanup and print results
        ret_msg += "Deleting temp dir: %s" % output_dir
        shutil.rmtree(output_dir)
        end_time = datetime.now()

        difftime = str(end_time - start_time)

        ret_msg += "Total time taken: %s events for %s: %s" % (str(counter),
                                                               target_date,
                                                               difftime)
        return ret_msg
