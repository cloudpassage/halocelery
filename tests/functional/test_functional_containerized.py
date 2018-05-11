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

    def test_firewall_graph_latest(self):
        container = self.build_containerized_object()
        resp = container.generate_firewall_graph(firewall_group)
        assert isinstance(resp, basestring)
        assert len(resp) > 1000  # This gives us a lot of b64-encoded info.

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
