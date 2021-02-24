from .utility import Utility
import docker
import os
import uuid


class Containerized(object):
    """All containerized tasks are launched from this class."""
    def __init__(self):
        self.client = docker.from_env()
        self.mem_limit = os.getenv('CONTAINER_MEM_LIMIT', '256m')

    def generic_container_launch_attached(self, image, env_vars, env_expand,
                                          read_only=True):
        """Launch a container, return the output from container's STDOUT.

        Containers launched by this method should return base64-enceded data.
        Extra newline characters can sometimes be added by Docker in addition
        to those present in the actual container output. As such, any newline
        characters will be stripped from the container's output before
        returning to the calling function.


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
        env_vars = self.expand_and_update_env_vars(env_vars.copy(),
                                                   env_expand.copy())
        Utility.log_stdout("ContainerLauncher: Launching %s from %s" %
                           (container_name, image))
        result = self.client.containers.run(image, name=container_name,
                                            detach=False,
                                            mem_limit=self.mem_limit,
                                            environment=env_vars)
        self.client.containers.get(container_name).remove()
        return result.replace("\n", "")

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
