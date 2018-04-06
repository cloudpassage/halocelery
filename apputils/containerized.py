import docker
import os


class Containerized(object):
    """All containerized tasks are launched from this class."""
    def __init__(self):
        self.client = docker.from_env()
        self.aws_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.halo_key = os.getenv('HALO_API_KEY')
        self.halo_secret = os.getenv('HALO_API_SECRET_KEY')
        self.mem_limit = os.getenv('CONTAINER_MEM_LIMIT')
        """Versions for containerized tasks.  Default to latest image."""
        self.ec2_halo_delta_ver = os.getenv('EC2_HALO_DELTA_VERSION', 'latest')
        self.fw_graph_ver = os.getenv('FIREWALL_GRAPH_VERSION', 'latest')
        self.vuln_image_ver = os.getenv('VULN_IMAGE_VERSION', 'latest')
        self.scans_to_s3_ver = os.getenv('SCANS_TO_S3_VERSION', 'latest')
        self.events_to_s3_ver = os.getenv('EVENTS_TO_S3_VERSION', 'latest')


    def halo_ec2_footprint_csv(self):
        image = ("docker.io/halotools/ec2-halo-delta:%s"
                 % self.ec2_halo_delta_ver)
        container_name = "ec2_halo_footprint"
        environment = {
            "HALO_API_KEY": self.halo_key,
            "HALO_API_SECRET_KEY": self.halo_secret,
            "AWS_ACCESS_KEY_ID": self.aws_key,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret,
            "OUTPUT_FORMAT": "csv"
        }

        # Populate optional fields to support multi-account inventory.
        optional_fields = ["AWS_ROLE_NAME", "AWS_ACCOUNT_NUMBERS"]
        for field in optional_fields:
            if os.getenv(field, "") != "":
                environment[field] = os.getenv(field)
        # Remove the container by name if it still exists from a prior run.
        try:
            self.client.containers.get(container_name).remove()
        except docker.errors.APIError:
            pass
        result = self.client.containers.run(image, name=container_name,
                                            detach=False,
                                            mem_limit=self.mem_limit,
                                            environment=environment)
        self.client.containers.get(container_name).remove()
        return result.replace('\n', '')

    def generate_firewall_graph(self, target):
        image = ("docker.io/halotools/firewall-graph:%s"
                 % self.fw_graph_ver)
        container_name = "halo_firewall_graph"
        environment = {
            "HALO_API_KEY": self.halo_key,
            "HALO_API_SECRET_KEY": self.halo_secret,
            "TARGET": target
        }

        # Remove the container by name if it still exists from a prior run.
        try:
            self.client.containers.get(container_name).remove()
        except docker.errors.APIError:
            pass
        result = self.client.containers.run(image, name=container_name,
                                            detach=False,
                                            mem_limit=self.mem_limit,
                                            environment=environment)
        self.client.containers.get(container_name).remove()
        return result.replace('\n', '')

    def scans_to_s3(self, target_date, s3_bucket_name):
        image = ("docker.io/halotools/halo-scans-archiver:%s"
                 % self.scans_to_s3_ver)
        container_name = "halo_scans_to_s3"
        environment = {
            "HALO_API_KEY": self.halo_key,
            "HALO_API_SECRET_KEY": self.halo_secret,
            "TARGET_DATE": target_date,
            "AWS_S3_BUCKET": s3_bucket_name,
            "AWS_ACCESS_KEY_ID": self.aws_key,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret
        }

        # Remove the container by name if it still exists from a prior run.
        try:
            self.client.containers.get(container_name).remove()
        except docker.errors.APIError:
            pass
        result = self.client.containers.run(image, name=container_name,
                                            detach=False,
                                            mem_limit=self.mem_limit,
                                            environment=environment)
        self.client.containers.get(container_name).remove()
        return result

    def events_to_s3(self, target_date, s3_bucket_name):
        image = ("docker.io/halotools/halo-events-archiver:%s" %
                 self.events_to_s3_ver)
        container_name = "halo_events_to_s3"
        environment = {
            "HALO_API_KEY": self.halo_key,
            "HALO_API_SECRET_KEY": self.halo_secret,
            "TARGET_DATE": target_date,
            "AWS_S3_BUCKET": s3_bucket_name,
            "AWS_ACCESS_KEY_ID": self.aws_key,
            "AWS_SECRET_ACCESS_KEY": self.aws_secret
        }

        # Remove the container by name if it still exists from a prior run.
        try:
            self.client.containers.get(container_name).remove()
        except docker.errors.APIError:
            pass
        result = self.client.containers.run(image, name=container_name,
                                            detach=False,
                                            mem_limit=self.mem_limit,
                                            environment=environment)
        self.client.containers.get(container_name).remove()
        return result

    def vulnerable_image_check(self):
        image = ("docker.io/halotools/vulnerable_image_check:%s" %
                 self.vuln_image_ver)
        container_name = "vulnerable_image_check"
        environment = {
            "HALO_API_KEY": self.halo_key,
            "HALO_API_SECRET_KEY": self.halo_secret,
            "OCTO_BOX": True
        }

        # Remove the container by name if it still exists from a prior run.
        try:
            self.client.containers.get(container_name).remove()
        except docker.errors.APIError:
            pass
        result = self.client.containers.run(image, name=container_name,
                                            detach=False,
                                            mem_limit=self.mem_limit,
                                            environment=environment)
        self.client.containers.get(container_name).remove()
        return result.replace('\n', '')
