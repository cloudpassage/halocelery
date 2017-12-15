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

    def halo_ec2_footprint_csv(self):
        image = "docker.io/halotools/ec2-halo-delta:v0.1"
        container_name = "ec2_halo_footprint"
        mem_limit = "256m"
        environment = {"HALO_API_KEY": self.halo_key,
                       "HALO_API_SECRET_KEY": self.halo_secret,
                       "AWS_ACCESS_KEY_ID": self.aws_key,
                       "AWS_SECRET_ACCESS_KEY": self.aws_secret,
                       "OUTPUT_FORMAT": "csv"}
        try:
            self.client.containers.get(container_name).remove()
        except docker.errors.APIError:
            pass
        result = self.client.containers.run(image, name=container_name,
                                            detach=False,
                                            mem_limit=mem_limit,
                                            environment=environment)
        self.client.containers.get(container_name).remove()
        return result.replace('\n', '')

    def scans_to_s3(self, target_date, s3_bucket_name):
        image = "docker.io/halotools/halo-scans-archiver:v0.14"
        container_name = "halo_scans_to_s3"
        mem_limit = "256m"
        environment = {"HALO_API_KEY": self.halo_key,
                       "HALO_API_SECRET_KEY": self.halo_secret,
                       "TARGET_DATE": target_date,
                       "AWS_S3_BUCKET": s3_bucket_name,
                       "AWS_ACCESS_KEY_ID": self.aws_key,
                       "AWS_SECRET_ACCESS_KEY": self.aws_secret}
        try:
            self.client.containers.get(container_name).remove()
        except docker.errors.APIError:
            pass
        result = self.client.containers.run(image, name=container_name,
                                            detach=False,
                                            mem_limit=mem_limit,
                                            environment=environment)
        self.client.containers.get(container_name).remove()
        return result

    def events_to_s3(self, target_date, s3_bucket_name):
        image = "docker.io/halotools/halo-events-archiver:v0.10"
        container_name = "halo_events_to_s3"
        mem_limit = "256m"
        environment = {"HALO_API_KEY": self.halo_key,
                       "HALO_API_SECRET_KEY": self.halo_secret,
                       "TARGET_DATE": target_date,
                       "AWS_S3_BUCKET": s3_bucket_name,
                       "AWS_ACCESS_KEY_ID": self.aws_key,
                       "AWS_SECRET_ACCESS_KEY": self.aws_secret}
        try:
            self.client.containers.get(container_name).remove()
        except docker.errors.APIError:
            pass
        result = self.client.containers.run(image, name=container_name,
                                            detach=False,
                                            mem_limit=mem_limit,
                                            environment=environment)
        self.client.containers.get(container_name).remove()
        return result
