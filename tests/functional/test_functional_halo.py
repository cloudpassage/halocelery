import cloudpassage
import os
import apputils


config_file_name = "portal.yaml"
tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
config_file = os.path.join(tests_dir, "configs/", config_file_name)

session_info = cloudpassage.ApiKeyManager(config_file=config_file)
key_id = session_info.key_id
secret_key = session_info.secret_key
api_hostname = session_info.api_hostname
api_port = session_info.api_port


class TestIntegrationHalo:
    def build_halo_object(self):
        return apputils.Halo()

    def test_list_all_servers(self):
        halo = self.build_halo_object()
        resp = halo.list_all_servers_formatted()
        assert "Server" and "Server ID" and "State" in resp

    def test_list_all_groups(self):
        halo = self.build_halo_object()
        resp = halo.list_all_groups_formatted()
        assert "Group" and "Group ID" and "Group Path" in resp

    def test_unable_to_generate_server_report(self):
        halo = self.build_halo_object()
        resp = halo.generate_server_report_formatted("123")
        assert resp == "Unable to find server 123"

    def test_generate_server_report_with_id(self):
        halo = self.build_halo_object()
        servers = cloudpassage.Server(halo.session).list_all()
        resp = halo.generate_server_report_formatted(servers[0]["id"])
        assert "Server" and "Server ID" and "State" in resp

    def test_unable_to_generate_group_report(self):
        halo = self.build_halo_object()
        resp = halo.generate_group_report_formatted("123")
        assert resp == "Unable to find group 123"

    def test_generate_group_report(self):
        halo = self.build_halo_object()
        groups = cloudpassage.ServerGroup(halo.session).list_all()
        resp = halo.generate_group_report_formatted(groups[0]["id"])
        assert "Group" and "Group ID" and "Group Path" in resp

    def test_get_id_for_group_invalid_target(self):
        halo = self.build_halo_object()
        resp = halo.get_id_for_group_target("xyzFoo")
        assert not resp

    def test_get_id_for_group_target(self):
        halo = self.build_halo_object()
        group = cloudpassage.ServerGroup(halo.session).list_all()[0]
        resp = halo.get_id_for_group_target(group["name"])
        assert resp == group["id"]

    def test_get_id_for_duplicate_group_target(self):
        halo = self.build_halo_object()
        grp_obj = cloudpassage.ServerGroup(halo.session)
        group = grp_obj.list_all()[0]
        new_grp_id = grp_obj.create(group["name"])
        resp = halo.get_id_for_group_target(group["name"])
        grp_obj.delete(new_grp_id)
        assert "Group" and "Group ID" and "Group Path" in resp

    def test_get_id_for_server_with_invalid_target(self):
        halo = self.build_halo_object()
        resp = halo.get_id_for_server_target("1234")
        assert not resp

    def test_get_id_for_server_with_target(self):
        halo = self.build_halo_object()
        servers = cloudpassage.Server(halo.session).list_all()
        resp = halo.get_id_for_server_target(servers[0]["hostname"])
        assert resp == servers[0]["id"]

    def test_add_ip_to_invalid_zone(self):
        halo = self.build_halo_object()
        resp = halo.add_ip_to_zone("127.0.0.1", "xyzFoo")
        assert resp == "Unable to find ID for IP zone xyzFoo!\n"

    def test_add_remove_ip_to_valid_zone(self):
        halo = self.build_halo_object()
        zone_obj = cloudpassage.FirewallZone(halo.session)
        all_zones = zone_obj.list_all()
        zone = self.get_valid_zone(all_zones)
        ip_address = '1.1.1.1'
        resp = halo.add_ip_to_zone(ip_address, zone["name"])
        assert resp == "Added IP address %s to zone ID %s\n" % (ip_address,
                                                                zone["name"])
        resp = halo.add_ip_to_zone(ip_address, zone["name"])
        assert resp == "IP address %s already in zone %s !\n" % (ip_address,
                                                                 zone["name"])

        resp = halo.remove_ip_from_zone(ip_address, zone["name"])
        assert resp == "Removed IP %s from zone %s\n" % (ip_address,
                                                         zone["name"])

    def test_remove_invalid_ip_from_zone(self):
        halo = self.build_halo_object()
        zone_obj = cloudpassage.FirewallZone(halo.session)
        all_zones = zone_obj.list_all()
        zone = self.get_valid_zone(all_zones)
        ip_address = 'a.b.c.d'
        resp = halo.remove_ip_from_zone(ip_address, zone["name"])
        assert resp == "IP %s was not found in zone %s\n" % (ip_address,
                                                             zone["name"])

    def get_valid_zone(self, all_zones):
        for zone in all_zones:
            if zone["name"] != "any":
                return zone
