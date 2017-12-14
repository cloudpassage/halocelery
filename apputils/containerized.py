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
        mem_limit = "256m"
        environment = {"HALO_API_KEY": self.halo_key,
                       "HALO_API_SECRET_KEY": self.halo_secret,
                       "AWS_ACCESS_KEY_ID": self.aws_key,
                       "AWS_SECRET_ACCESS_KEY": self.aws_secret,
                       "OUTPUT_FORMAT": "csv"}
        result = self.client.containers.run(image, name="ec2_halo_footprint",
                                            auto_remove=True,
                                            detach=False,
                                            mem_limit=mem_limit,
                                            environment=environment)
        return result
