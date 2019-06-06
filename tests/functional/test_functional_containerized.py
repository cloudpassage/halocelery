import imp
import os
import sys


module_name = 'apputils'
here_dir = os.path.dirname(os.path.abspath(__file__))
module_path = os.path.join(here_dir, '../../')
sys.path.append(module_path)
fp, pathname, description = imp.find_module(module_name)
apputils = imp.load_module(module_name, fp, pathname, description)

firewall_group = os.getenv("FIREWALL_GRAPH_GROUP")


class TestIntegrationContainerized:
    def build_containerized_object(self):
        return apputils.Containerized()

    def test_name_generator(self):
        sample = set({})
        for x in range(1000):
            sample.add(apputils.Containerized.generate_random_name())
        assert len(sample) == 1000

    def test_expand_env_vars(self, monkeypatch):
        monkeypatch.setenv("FOO", "BAD")
        monkeypatch.setenv("BAR", "BAZ")
        in_vars = {"HELLO": "WORLD"}
        in_exp_vars = {"FOO": "BAR"}
        out = apputils.Containerized.expand_and_update_env_vars(in_vars,
                                                                in_exp_vars)
        assert out["FOO"] == "BAZ"
        assert out["HELLO"] == "WORLD"

    def test_generic_containerized_task(self):
        img_tag = os.getenv('FIREWALL_GRAPH_VERSION', 'latest')
        image = "docker.io/halotools/firewall-graph:%s" % img_tag
        cont = apputils.Containerized()
        env_literal = {"TARGET": firewall_group}
        env_expand = {"HALO_API_KEY": "HALO_API_KEY",
                      "HALO_API_SECRET_KEY": "HALO_API_SECRET_KEY",
                      "HALO_API_HOSTNAME": "HALO_API_HOSTNAME",
                      "HTTPS_PROXY": "HTTPS_PROXY"}
        results = cont.generic_container_launch_attached(image, env_literal,
                                                         env_expand, False)
        assert len(results) > 100  # We get a lot of base64 back.
