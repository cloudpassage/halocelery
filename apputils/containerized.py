import docker
import os
import uuid


class Containerized(object):
    """All containerized tasks are launched from this class."""
    def __init__(self):
        self.client = docker.from_env()
        self.aws_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.halo_key = os.getenv('HALO_API_KEY')
        self.halo_secret = os.getenv('HALO_API_SECRET_KEY')
        self.mem_limit = os.getenv('CONTAINER_MEM_LIMIT')
        self.https_proxy = os.getenv('HTTPS_PROXY')
        """Versions for containerized tasks.  Default to latest image."""
        self.ec2_halo_delta_ver = os.getenv('EC2_HALO_DELTA_VERSION', 'latest')
        self.fw_graph_ver = os.getenv('FIREWALL_GRAPH_VERSION', 'latest')
        self.scans_to_s3_ver = os.getenv('SCANS_TO_S3_VERSION', 'latest')
        self.events_to_s3_ver = os.getenv('EVENTS_TO_S3_VERSION', 'latest')

    def generic_container_launch_attached(self, image, env_vars, env_expand,
                                          read_only=True):
        """Launch a container, return the output from container's STDOUT.


        Args:
            image(str): Full image path. For example:
                ``docker.io/halotools/halocelery:latest``
            env_vars(dict): Environment variables in a dictionary where key
                and value are ``{'key1': 'value1', 'key2': 'value2'}``
            env_expand(dict): Environment variable names (as seen inside the
                container) are keys and the values are to be expanded from the
                environment variables available to the running celery worker.
                For instance, if the container needs an environment variable
                named ``FOO`` to contain the value of the celery worker's
                environment variable named ``BAR``, this argument would take
                the form of ``{'FOO': 'BAR'}``. If the celery worker has an
                environment variable named ``BAR``, which contains the value
                ``BAZ``, and arg:env_expanded is ``{'FOO': 'BAR'}``, the
                environment inside the running container will contain an
                environment variable named ``FOO`` with the value ``BAZ``.
                In short, the keys are persisted into the container and the
                values are replaced with the corresponding environment
                variables, according to the environment running celery.
            read_only(bool): Set to ``False`` to allow writeable access to
                filesystem inside container.

        """
        container_name = self.generate_random_name()
        env_vars = self.expand_and_update_env_vars(env_vars, env_expand)
        print("ContainerLauncher: Launching %s from %s" % (container_name,
                                                           image))
        result = self.client.containers.run(image, name=container_name,
                                            detach=False,
                                            mem_limit=self.mem_limit,
                                            environment=env_vars)
        self.client.containers.get(container_name).remove()
        return result

    @classmethod
    def generate_random_name(cls):
        """Generate a string for naming containers."""
        retval = str(uuid.uuid1()).replace("-", "")
        return retval

    @classmethod
    def expand_and_update_env_vars(cls, env_vars, env_expand):
        """Return a dict object where values are expanded env vars.

        Args:
            env_vars(dict): This dict is updated by arg:env_expanded
            env_expanded(dict): Keys are retained, values are expanded.
        """
        for k, v in env_expand.items():
            env_vars[k] = os.getenv(v, "")
        return env_vars.copy()

    def halo_ec2_footprint_csv(self):
        image = ("docker.io/halotools/ec2-halo-delta:%s"
                 % self.ec2_halo_delta_ver)
        env_expand = {"HALO_API_KEY": "HALO_API_KEY",
                      "HALO_API_SECRET_KEY": "HALO_API_SECRET_KEY",
                      "AWS_ACCESS_KEY_ID": "AWS_ACCESS_KEY_ID",
                      "AWS_SECRET_ACCESS_KEY": "AWS_SECRET_ACCESS_KEY",
                      "HTTPS_PROXY": "HTTPS_PROXY"}
        env_vars = {"OUTPUT_FORMAT": "csv"}
        # Populate optional fields to support multi-account inventory.
        optional_fields = ["AWS_ROLE_NAME", "AWS_ACCOUNT_NUMBERS"]
        for field in optional_fields:
            if os.getenv(field, "") != "":
                env_vars[field] = os.getenv(field)
        result = self.generic_container_launch_attached(image, env_vars,
                                                        env_expand)
        return result.replace('\n', '')

    def generate_firewall_graph(self, target):
        image = ("docker.io/halotools/firewall-graph:%s" % self.fw_graph_ver)
        env_vars = {"TARGET": target}
        env_expand = {"HALO_API_KEY": "HALO_API_KEY",
                      "HALO_API_SECRET_KEY": "HALO_API_SECRET_KEY",
                      "HTTPS_PROXY": "HTTPS_PROXY"}
        result = self.generic_container_launch_attached(image, env_vars,
                                                        env_expand, False)
        return result.replace('\n', '')

    def scans_to_s3(self, target_date, s3_bucket_name):
        image = ("docker.io/halotools/halo-scans-archiver:%s"
                 % self.scans_to_s3_ver)
        env_vars = {"TARGET_DATE": target_date,
                    "AWS_S3_BUCKET": s3_bucket_name}
        env_expand = {"HALO_API_KEY": "HALO_API_KEY",
                      "HALO_API_SECRET_KEY": "HALO_API_SECRET_KEY",
                      "AWS_ACCESS_KEY_ID": "AWS_ACCESS_KEY_ID",
                      "AWS_SECRET_ACCESS_KEY": "AWS_SECRET_ACCESS_KEY",
                      "HTTPS_PROXY": "HTTPS_PROXY"}
        result = self.generic_container_launch_attached(image, env_vars,
                                                        env_expand, False)
        return result

    def events_to_s3(self, target_date, s3_bucket_name):
        image = ("docker.io/halotools/halo-events-archiver:%s" %
                 self.events_to_s3_ver)
        env_vars = {"TARGET_DATE": target_date,
                    "AWS_S3_BUCKET": s3_bucket_name}
        env_expand = {"HALO_API_KEY": "HALO_API_KEY",
                      "HALO_API_SECRET_KEY": "HALO_API_SECRET_KEY",
                      "AWS_ACCESS_KEY_ID": "AWS_ACCESS_KEY_ID",
                      "AWS_SECRET_ACCESS_KEY": "AWS_SECRET_ACCESS_KEY",
                      "HTTPS_PROXY": "HTTPS_PROXY"}

        result = self.generic_container_launch_attached(image, env_vars,
                                                        env_expand, False)
        return result
