import os
import sys
import imp


module_name = 'apputils'
here_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(here_dir, '../../')
sys.path.append(module_path)
fp, pathname, description = imp.find_module(module_name)
apputils = imp.load_module(module_name, fp, pathname, description)


class TestUnitHalo:
    def test_instantiation(self):
        assert apputils.Halo()

    def server_data(self):
        data = {
            "created_at": "2018-03-01T20:08:37.233Z",
            "id": "53bd2b9e1d8c11e88ab75dca3f0e16e7",
            "hostname": "ip-172-31-1-229",
            "server_label": "ip-172-31-1-229",
            "reported_fqdn": "ip-172-31-1-229.us-west-2.compute.internal",
            "primary_ip_address": "172.31.1.229",
            "connecting_ip_address": "34.217.116.155",
            "state": "active",
            "daemon_version": "4.1.6",
            "read_only": False,
            "platform": "amazon",
            "platform_version": "2016.09",
            "os_version": "4.4.23-31.54.amzn1.x86_64",
            "kernel_name": "Linux",
            "kernel_machine": "x86_64",
            "self_verification_failed": False,
            "last_state_change": "2018-03-01T20:08:37.233Z",
            "group_id": "cfc443e0dbe90132fdd73c764e10c221",
            "group_name": "CloudPassage (Customer Success)",
            "group_path": "CloudPassage (Customer Success)",
            "interfaces": [
                {
                    "name": "eth0",
                    "ip_address": "FE80::864:E1FF:FEBB:976A/64",
                    "netmask": "",
                    "mac_address": None
                },
                {
                    "name": "eth0",
                    "ip_address": "172.31.1.229",
                    "netmask": "255.255.240.0",
                    "mac_address": None
                }
            ],
            "aws_ec2": {
                "ec2_instance_id": "i-0c3033c3fc8e39510",
                "ec2_account_id": "776183744304",
                "ec2_kernel_id": "aki-fc8f11cc",
                "ec2_image_id": "ami-a4bc1bc4",
                "ec2_availability_zone": "us-west-2c",
                "ec2_region": "us-west-2",
                "ec2_private_ip": "172.31.1.229",
                "ec2_instance_type": "t1.micro",
                "ec2_security_groups": [
                    "awseb-e-wgrpsxxhvt-stack-AWSEBSecurityGroup-IBGM2VY0LR4M"
                ]
            }
        }
        return data

    def test_flatten_ec2(self):
        data = self.server_data()
        halo = apputils.Halo()
        flatten_data = halo.flatten_ec2(data)
        assert flatten_data["ec2_instance_id"]
