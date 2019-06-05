import cloudpassage
import os
import re
from utility import Utility as util
from formatter import Formatter as fmt
from utility import Utility


class Halo(object):
    def __init__(self):
        self.halo_api_key = os.getenv("HALO_API_KEY")
        self.halo_api_secret = os.getenv("HALO_API_SECRET_KEY")
        self.halo_api_key_rw = os.getenv("HALO_API_KEY_RW")
        self.halo_api_secret_rw = os.getenv("HALO_API_SECRET_KEY_RW")
        self.halo_api_host = os.getenv("HALO_API_HOSTNAME")
        self.integration_string = self.get_integration_string()
        self.session = cloudpassage.HaloSession(self.halo_api_key,
                                                self.halo_api_secret,
                                                api_host=self.halo_api_host,
                                                integration_string=self.integration_string)
        self.rw_session = cloudpassage.HaloSession(self.halo_api_key_rw,
                                                   self.halo_api_secret_rw,
                                                   api_host=self.halo_api_host,
                                                   integration_string=self.integration_string)

    def list_all_servers_formatted(self):
        """Return a list of all servers, formatted for Slack."""
        servers = cloudpassage.Server(self.session)
        return fmt.format_list(servers.list_all(), "server_facts")

    def list_all_groups_formatted(self):
        """Return a list of all groups, formatted for Slack."""
        groups_obj = cloudpassage.ServerGroup(self.session)
        g_ids = [x["id"] for x in groups_obj.list_all()]
        groups = [self.flatten_group(groups_obj.describe(x)) for x in g_ids]
        return fmt.format_list(groups, "group_facts")

    def generate_server_report_formatted(self, target):
        """Return a formatted server report for arg:target server."""
        server_ids = self.get_id_for_server_target(target)
        result = ""
        if len(server_ids) == 0:
            return "Unable to find server %s" % target
        for server_id in server_ids:
            Utility.log_stdout("ServerReport: Starting report for %s" % server_id)  # NOQA
            server_obj = cloudpassage.Server(self.session)
            Utility.log_stdout("ServerReport: Getting server facts")
            facts = self.flatten_ec2(server_obj.describe(server_id))
            if "aws_ec2" in facts:
                result = fmt.format_item(facts, "server_ec2")
            else:
                result = fmt.format_item(facts, "server_facts")
            Utility.log_stdout("ServerReport: Getting server issues")
            result += fmt.format_list(self.get_issues_by_server(server_id),
                                      "issue")
            Utility.log_stdout("ServerReport: Getting server events")
            result += fmt.format_list(self.get_events_by_server(server_id),
                                      "event")
        return result

    def generate_group_report_formatted(self, target):
        """Return a group report for group indicated by arg:target.

        In the event multiple groups match arg:target by name, this function
        returns a formatted report for all groups with a matching name.

        Args:
            target(str): Name or ID of server group.

        """
        group_ids = self.get_id_for_group_target(target)
        result = ""
        if len(group_ids) == 0:
            return "Unable to find group %s" % target
        for g_id in group_ids:
            group_obj = cloudpassage.ServerGroup(self.session)
            grp_struct = group_obj.describe(g_id)
            facts = self.flatten_group(grp_struct)
            result = fmt.format_item(facts, "group_facts")
            result += self.get_group_policies(facts)
            Utility.log_stdout("IssueReport: Getting group issues")
            result += fmt.format_list(self.get_issues_by_group(g_id),
                                      "grp_issue")
        return result

    def get_group_policies(self, grp_struct):
        """Return a formatted list of policies, derived from arg:grp_struct.
        """
        retval = ""
        firewall_keys = ["firewall_policy_id", "windows_firewall_policy_id"]
        csm_keys = ["policy_ids", "windows_policy_ids"]
        fim_keys = ["fim_policy_ids", "windows_fim_policy_ids"]
        lids_keys = ["lids_policy_ids"]
        Utility.log_stdout("Getting meta for FW policies")
        for fwp in firewall_keys:
            retval += self.get_policy_metadata(grp_struct[fwp], "FW")
        Utility.log_stdout("Getting meta for CSM policies")
        for csm in csm_keys:
            retval += self.get_policy_list(grp_struct[csm], "CSM")
        Utility.log_stdout("Getting meta for FIM policies")
        for fim in fim_keys:
            retval += self.get_policy_list(grp_struct[fim], "FIM")
        Utility.log_stdout("Getting meta for LIDS policies")
        for lids in lids_keys:
            retval += self.get_policy_list(grp_struct[lids], "LIDS")
        Utility.log_stdout("Gathered all policy metadata successfully")
        return retval

    def get_policy_list(self, policy_ids, policy_type):
        """Get a formatted list of policies by ID and type.

        Args:
            policy_ids(list): List of policy IDs.
            policy_type(str): Policy type. See ``p_ref`` in
                ``get_policy_metadata()`` for supported policy types.
        """
        retval = ""
        for policy_id in policy_ids:
            retval += self.get_policy_metadata(policy_id, policy_type)
        return retval

    def get_policy_metadata(self, policy_id, policy_type):
        """Return formatted policy metadata.

        Args:
            policy_id(str): ID for Halo policy.
            policy_type(str): Type of policy.  Must be included in ``p_ref``,
                or an empty string will be returned.
        """
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
        """Return a list of IDs for groups matching arg:target.

        Attempts to get group_id using arg:target as group_name, then by id.

        Args:
            target(str): Name or ID of group.

        Returns:
            list: List of group IDs

        """
        group = cloudpassage.ServerGroup(self.session)
        orig_result = group.list_all()
        try:  # See if we've been given a group ID
            result = [(group.describe(target))["id"]]
        except cloudpassage.CloudPassageResourceExistence:
            # Get a list of all matching groups
            result = [x["id"] for x in orig_result if x["name"] == target]
        return result

    def get_id_for_server_target(self, target):
        """Return a list of IDs for servers matching arg:target.

        Attempts to get server_id using arg:target as hostname, then id.

        Args:
            target(str): Server ID or server name.

        Returns:
            list: List of server IDs
        """
        server = cloudpassage.Server(self.session)
        try:
            result = [server.describe(target)["id"]]
        except cloudpassage.CloudPassageResourceExistence:
            result = [x["id"] for x in server.list_all(hostname=target)]
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
        """Return all issues for server identified by arg:server_id."""
        pagination_key = 'issues'
        url = '/v2/issues'
        params = {
            'agent_id': server_id,
            'status': 'active'
        }
        hh = cloudpassage.HttpHelper(self.session)
        issues = hh.get_paginated(url, pagination_key, 5, params=params)
        return issues

    def get_issues_by_group(self, group_id):
        """Return all issues for group identified by arg:group_id."""
        pagination_key = 'issues'
        url = '/v2/issues'
        params = {
            'group_id': group_id,
            'status': 'active',
            'group_by': 'rule_key,issue_type,critical',
            'sort_by': 'critical.desc',
            'descendants': 'true'
        }
        hh = cloudpassage.HttpHelper(self.session)
        issues = hh.get_paginated(url, pagination_key, 5, params=params)
        return issues

    def list_servers_in_group_formatted(self, target):
        """Return a list of servers in group after sending through formatter.

        If more than one group matches arg:target, a report for all matching
        groups will be returned.

        Args:
            target(str): Group ID or name.
        """
        group = cloudpassage.ServerGroup(self.session)
        group_ids = self.get_id_for_group_target(target)
        reports = [fmt.format_list(group.list_members(g_id), "server_facts")
                   for g_id in group_ids]
        if len(reports) == 0:
            msg = "No matching groups found!"
        elif len(reports) > 1:
            msg = "Multiple matching groups found...\n\n"
            msg += "\n\n--------\n\n".join(reports)
        else:
            msg = reports[0]
        return msg

    def get_server_by_cve(self, cve):
        """Return a formatted list of servers having CVE.

        Args:
            cve(str): CVE ID to search for.
        """
        pagination_key = 'servers'
        url = '/v1/servers'
        params = {'cve': cve}
        hh = cloudpassage.HttpHelper(self.session)
        servers = hh.get_paginated(url, pagination_key, 5, params=params)
        message = "Server(s) that contain CVE: %s\n" % cve
        message += fmt.format_list(servers, "server_facts")
        return message

    def move_server(self, server_id, group_id):
        """Silence is golden.  If it doesn't throw an exception, it worked."""
        server_obj = cloudpassage.Server(self.rw_session)
        server_obj.assign_group(server_id, group_id)

    def get_id_for_ip_zone(self, ip_zone_name):
        """Return ID for IP zone indicated by arg:ip_zone_name."""
        zone_obj = cloudpassage.FirewallZone(self.session)
        all_zones = zone_obj.list_all()
        for zone in all_zones:
            if zone["name"] == ip_zone_name:
                return zone["id"]
        return None

    def add_ip_to_zone(self, ip_address, zone_name):
        """Add an IP address to IP zone.


        Args:
            ip_address(str): IP address to be added to zoneself.
            zone_name(str):Name of IP zone to add arg:ip_address to.
        """
        update_zone = {"firewall_zone": {"name": zone_name}}
        zone_obj = cloudpassage.FirewallZone(self.rw_session)
        zone_id = self.get_id_for_ip_zone(zone_name)
        if zone_id is None:
            msg = "Unable to find ID for IP zone %s!\n" % zone_name
            return msg
        else:
            update_zone["firewall_zone"]["id"] = zone_id
        existing_zone = zone_obj.describe(zone_id)
        existing_ips = util.ipaddress_list_from_string(existing_zone["ip_address"])  # NOQA
        if ip_address in existing_ips:
            msg = "IP address %s already in zone %s !\n" % (ip_address,
                                                            zone_name)
        else:
            existing_ips.append(ip_address)
            update_zone["firewall_zone"]["ip_address"] = util.ipaddress_string_from_list(existing_ips)  # NOQA
            zone_obj.update(update_zone)
            msg = "Added IP address %s to zone ID %s\n" % (ip_address,
                                                           zone_name)
        return msg

    def remove_ip_from_zone(self, ip_address, zone_name):
        """Remove IP address from IP zone.

        Args:
            ip_address(str): IP address to be removed from IP zone.
            zone_name(str): Name of IP zone to remove arg:ip_address from.
        """
        update_zone = {"firewall_zone": {"name": zone_name}}
        zone_obj = cloudpassage.FirewallZone(self.rw_session)
        zone_id = self.get_id_for_ip_zone(zone_name)
        if zone_id is None:
            msg = "Unable to find ID for IP zone %s!\n" % zone_name
            return msg
        else:
            update_zone["firewall_zone"]["id"] = zone_id
        existing_zone = zone_obj.describe(zone_id)
        existing_ips = util.ipaddress_list_from_string(existing_zone["ip_address"])  # NOQA
        try:
            existing_ips.remove(ip_address)
            update_zone["firewall_zone"]["ip_address"] = util.ipaddress_string_from_list(existing_ips)  # NOQA
            zone_obj.update(update_zone)
            msg = "Removed IP %s from zone %s\n" % (ip_address, zone_name)
        except ValueError:
            msg = "IP %s was not found in zone %s\n" % (ip_address, zone_name)
        return msg

    def get_integration_string(self):
        """Return integration string for this tool."""
        return "halocelery/%s" % self.get_tool_version()

    def get_tool_version(self):
        """Get version of this tool from the __init__.py file."""
        here_path = os.path.abspath(os.path.dirname(__file__))
        init_file = os.path.join(here_path, "__init__.py")
        ver = 0
        with open(init_file, 'r') as i_f:
            rx_compiled = re.compile(r"\s*__version__\s*=\s*\"(\S+)\"")
            ver = rx_compiled.search(i_f.read()).group(1)
        return ver

    @classmethod
    def flatten_ec2(cls, server):
        try:
            for k, v in server["aws_ec2"].items():
                server[k] = v
            if "ec2_security_groups" in server:
                conjoined = " ,".join(server["ec2_security_groups"])
                server["ec2_security_groups"] = conjoined
            return server
        except:
            return server

    @classmethod
    def flatten_group(cls, group):
        for k, v in group["server_counts"].items():
            group[k] = v
        return group
