'''
This module tests if the save_thread_result package can be
successfully built on different python versions in a
Docker image.

NOTE: this module MUST be called from inside
save_thread_result.python
and NOT from inside
save_thread_result.python.tests
for the Docker image to build correctly.
'''

import os

def main(
) -> None:
    environments = [
        'debian-bullseye-slim-python3_0-from_source',
        'debian-bullseye-slim-python3_1-from_source',
        'debian-bullseye-slim-python3_2-from_source',
        'debian-bullseye-slim-python3_3-from_source',
        'debian-bullseye-slim-python3_4-from_source',
        'debian-bullseye-slim-python3_5-from_source',
        'debian-bullseye-slim-python3_6-from_source',
        'debian-bullseye-slim-python3_7-from_source',
        'debian-bullseye-slim-python3_8-from_source',
        'debian-bullseye-slim-python3_9-from_source',
        'debian-bullseye-slim-python3_10-from_source',
        'debian-bullseye-slim-python3_11-from_source',
        'debian-bullseye-slim-python3_12-from_source',
    ]
    for environment in environments:
        dockerfile_location = ['.', 'dockerfiles', environment]
        build_docker_image(dockerfile_location)


def build_docker_image(
    dockerfile_location: str,
) -> None:
    formatted_dockerfile_location = os.path.join(*dockerfile_location)
    formatted_docker_image_tag = dockerfile_location[-1]
    os.system(f'docker build --tag save_thread_result-{formatted_docker_image_tag} --file {formatted_dockerfile_location} .')


if __name__ == '__main__':
    main()
