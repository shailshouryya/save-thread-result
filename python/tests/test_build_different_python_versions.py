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
        'debian-bullseye-20231120-slim-python3_0_1-from_source',
        'debian-bullseye-20231120-slim-python3_1_1-from_source',
        'debian-bullseye-20231120-slim-python3_2_6-from_source',
        'debian-bullseye-20231120-slim-python3_3_7-from_source',
        'debian-bullseye-20231120-slim-python3_4_10-from_source',
        'debian-bullseye-20231120-slim-python3_5_10-from_source',
        'debian-bullseye-20231120-slim-python3_6_15-from_source',
        'debian-bullseye-20231120-slim-python3_7_17-from_source',
        'debian-bullseye-20231120-slim-python3_8_18-from_source',
        'debian-bullseye-20231120-slim-python3_9_18-from_source',
        'debian-bullseye-20231120-slim-python3_10_13-from_source',
        'debian-bullseye-20231120-slim-python3_11_6-from_source',
        'debian-bullseye-20231120-slim-python3_12_0-from_source',
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
