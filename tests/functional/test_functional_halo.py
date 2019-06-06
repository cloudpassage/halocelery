import cloudpassage
import imp
import os
import sys


module_name = 'apputils'
here_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(here_dir, '../../')
sys.path.append(module_path)
fp, pathname, description = imp.find_module(module_name)
apputils = imp.load_module(module_name, fp, pathname, description)


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
        # Ensure all templated fields are populated
        assert "$total" not in resp
        assert "$active" not in resp
        assert "$missing" not in resp
        assert "$deactivated" not in resp

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
        assert group["id"] in resp

    def test_get_id_for_duplicate_group_target(self):
        halo = self.build_halo_object()
        resp = halo.get_id_for_group_target("duplicate")
        assert isinstance(resp, list)
        assert len(resp) > 1

    def test_get_id_for_server_with_invalid_target(self):
        halo = self.build_halo_object()
        resp = halo.get_id_for_server_target("1234")
        assert not resp

    def test_get_id_for_server_with_target(self):
        halo = self.build_halo_object()
        servers = cloudpassage.Server(halo.session).list_all()
        resp = halo.get_id_for_server_target(servers[0]["hostname"])
        assert servers[0]["id"] in resp

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

    def test_integration_string(self):
        """Test to verify integration_string is constructed correctly"""
        halo = self.build_halo_object()
        assert halo.integration_string == "halocelery/%s" % apputils.__version__
