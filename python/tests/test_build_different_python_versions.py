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

from typing import (
    Sequence,
)

def main(
) -> None:
    environments = [
        'template-debian-bullseye-slim-python-MAJOR_MINOR-from_source-version_0',
        'template-debian-bullseye-slim-python-MAJOR_MINOR-from_source-version_legacy_1',
    ]
    for environment in environments:
        dockerfile_template_location = ['.', 'dockerfiles', environment]
        write_dockerfiles(dockerfile_template_location)
    for directory, _, files in os.walk('.'):
        files.sort() # go through files in sorted order by name
        for file in files:
            if file.startswith('from_template-'):
                dockerfile_location = os.path.join(directory, file)
                build_docker_image(dockerfile_location)


def read_file(
    file_location: Sequence[str]
) -> str:
    formatted_dockerfile_template_location = os.path.join(*file_location)
    with open(file=formatted_dockerfile_template_location, mode='r', buffering=-1, encoding='utf-8', newline=None) as file:
        return file.read()

def write_dockerfiles(
    dockerfile_template_location: Sequence[str],
) -> None:
    formatted_dockerfile_template_location = os.path.join(*dockerfile_template_location)
    dockerfile_template                    = read_dockerfile_template(formatted_dockerfile_template_location)
    dockerfile_template_for_versions       = dockerfile_template_location[::] # make a copy to avoid modifying original object
    dockerfile_template_for_versions[-1]  += '-versions'                      #
    formatted_dockerfile_template_for_versions = os.path.join(*dockerfile_template_for_versions)
    with open(file=formatted_dockerfile_template_for_versions, mode='r', buffering=-1, encoding='utf-8', newline=None) as dockerfile_template_for_versions_file:
        for build_version in dockerfile_template_for_versions_file:
            write_dockerfile_from_template(build_version, dockerfile_template, formatted_dockerfile_template_location)

def read_dockerfile_template(
    formatted_dockerfile_template_location: str,
) -> str:
    with open(formatted_dockerfile_template_location, mode='r', buffering=-1, encoding='utf-8', newline=None) as file:
        dockerfile_template = file.read()
    return dockerfile_template

def write_dockerfile_from_template(
    build_version: str,
    dockerfile_template: str,
    formatted_dockerfile_template_location: str,
) -> None:
    build_version             = build_version.strip()
    major_minor               = '.'.join(build_version.split('.')[:-1:]) # remove the patch version
    formatted_major_minor     = major_minor.replace('.', '_')
    dockerfile_write_location = formatted_dockerfile_template_location.replace('-MAJOR_MINOR', formatted_major_minor).replace('template', f'from_template-{formatted_major_minor}').split('-version_')[0]
    with open(file=dockerfile_write_location, mode='w', buffering=-1, encoding='utf-8', newline=None) as file:
        file.write(dockerfile_template.format(MAJOR_MINOR_PATCH=build_version, MAJOR_MINOR=major_minor))


def build_docker_image(
    dockerfile_location: str,
) -> None:
    docker_tag_base = dockerfile_location.split('from_template-')[-1]
    # print(docker_tag_base, dockerfile_location)
    os.system(f'docker build --tag save_thread_result-{docker_tag_base} --file {dockerfile_location} .')


if __name__ == '__main__':
    main()
