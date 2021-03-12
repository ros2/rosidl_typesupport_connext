# Copyright 2021 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pathlib
import subprocess

from ament_index_python import get_package_share_directory

from rosidl_cli.command.generate.extensions import GenerateCommandExtension
from rosidl_cli.command.helpers import generate_visibility_control_file
from rosidl_cli.command.helpers import idl_tuples_from_interface_files
from rosidl_cli.command.helpers import legacy_generator_arguments_file
from rosidl_cli.command.translate.api import translate

from rosidl_typesupport_connext_cpp import generate_cpp
from rosidl_typesupport_connext_cpp import generate_dds_connext_cpp_file


def find_rti_connext_idl_preprocessor():
    if os.name == 'nt':
        if 'NDDSHOME' not in os.environ:
            raise RuntimeError('"NDDSHOME" not set')
        nddshome = os.environ['NDDSHOME']
        ddsgen = os.path.join(nddshome, 'bin', 'rtiddsgen.bat')
        ddsgen_server = os.path.join(nddshome, 'bin', 'rtiddsgen_server.bat')
    else:
        nddshome = os.environ.get('NDDSHOME', '/usr')
        ddsgen = os.path.join(nddshome, 'bin', 'rtiddsgen')
        ddsgen_server = os.path.join(nddshome, 'bin', 'rtiddsgen_server')
    if os.path.exists(ddsgen_server):
        proc = subprocess.run([ddsgen_server, '-n_version'])
        if proc.returncode == 0:
            return ddsgen_server
    if not os.path.exists(ddsgen):
        raise RuntimeError(f'{ddsgen} could not be found')
    return ddsgen


class GenerateDDSConnextCpp(GenerateCommandExtension):

    def generate(
        self,
        package_name,
        interface_files,
        include_paths,
        output_path
    ):
        idl_pp = find_rti_connext_idl_preprocessor()

        # Normalize interface definition format to _.idl
        dds_idl_interface_files = []
        non_dds_idl_interface_files = []
        for path in interface_files:
            if not path.endswith('_.idl'):
                non_dds_idl_interface_files.append(path)
            else:
                dds_idl_interface_files.append(path)
        if non_dds_idl_interface_files:
            dds_idl_interface_files.extend(translate(
                package_name=package_name,
                interface_files=non_dds_idl_interface_files,
                include_paths=include_paths,
                output_format='dds_idl',
                output_path=output_path / 'tmp',
            ))

        generated_files = []
        for idl_tuple in idl_tuples_from_interface_files(
            dds_idl_interface_files
        ):
            prefix, _, stem = idl_tuple.rpartition(':')
            idl_file = os.path.join(prefix, stem)

            output_dir = os.path.join(
                output_path, os.path.dirname(stem))
            os.makedirs(output_dir, exist_ok=True)

            # Generate RTI Connext specific code
            generated_files.extend(generate_dds_connext_cpp_file(
                package_name, idl_file, include_paths, output_dir, idl_pp
            ))

        return generated_files


class GenerateConnextCppTypesupport(GenerateCommandExtension):

    def generate(
        self,
        package_name,
        interface_files,
        include_paths,
        output_path
    ):
        generated_files = []

        package_share_path = pathlib.Path(
            get_package_share_directory('rosidl_typesupport_connext_cpp'))
        templates_path = package_share_path / 'resource'

        # Normalize interface definition format to .idl
        idl_interface_files = []
        non_idl_interface_files = []
        for path in interface_files:
            if not path.endswith('.idl'):
                non_idl_interface_files.append(path)
            else:
                idl_interface_files.append(path)
        if non_idl_interface_files:
            idl_interface_files.extend(translate(
                package_name=package_name,
                interface_files=non_idl_interface_files,
                include_paths=include_paths,
                output_format='idl',
                output_path=output_path / 'tmp',
            ))

        # Generate visibility control file
        visibility_control_file_template_path = \
            'rosidl_typesupport_connext_cpp__visibility_control.h.in'
        visibility_control_file_template_path = \
            templates_path / visibility_control_file_template_path
        visibility_control_file_path = \
            'rosidl_typesupport_connext_cpp__visibility_control.h'
        visibility_control_file_path = \
            output_path / 'msg' / visibility_control_file_path

        generate_visibility_control_file(
            package_name=package_name,
            template_path=visibility_control_file_template_path,
            output_path=visibility_control_file_path
        )
        generated_files.append(visibility_control_file_path)

        with legacy_generator_arguments_file(
            package_name=package_name,
            interface_files=idl_interface_files,
            include_paths=include_paths,
            templates_path=templates_path,
            output_path=output_path
        ) as path_to_arguments_file:
            # Generate typesupport code
            generated_files.extend(generate_cpp(path_to_arguments_file))

        return generated_files
