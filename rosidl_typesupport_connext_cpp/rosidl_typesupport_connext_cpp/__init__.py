# Copyright 2014 Open Source Robotics Foundation, Inc.
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
import subprocess
import sys

from rosidl_cmake import generate_files
from convert_to_connext_idl import convert_to_connext_idl


def generate_dds_connext_cpp(pkg_name, dds_interface_files,
                             dds_interface_base_path,
                             output_basepath, idl_pp):
    include_dirs = [dds_interface_base_path]
    for index, idl_file in enumerate(dds_interface_files):
        assert os.path.exists(idl_file), 'Could not find IDL file: ' + idl_file
        # Get two level of parent folders for idl file
        folder = os.path.dirname(idl_file)
        parent_folder = os.path.dirname(folder)
        output_path = os.path.join(
            output_basepath,
            os.path.basename(parent_folder),
            os.path.basename(folder))
        try:
            os.makedirs(output_path)
        except FileExistsError:
            pass

        # Convert IDL file to a form that's compatible with what RTI Connext expects.
        converted_idl_file = convert_to_connext_idl(idl_file, dds_interface_base_path)

        cmd = [idl_pp]
        for include_dir in include_dirs:
            cmd += ['-I', include_dir]
        cmd += [
            '-d', output_path,
            '-language', 'C++',
            '-namespace',
            '-update', 'typefiles',
            '-unboundedSupport',
            converted_idl_file
        ]
        if os.name == 'nt':
            cmd[-5:-5] = ['-dllExportMacroSuffix', pkg_name]

        msg_name = os.path.splitext(os.path.basename(idl_file))[0]
        count = 1
        max_count = 5
        while True:
            subprocess.check_call(cmd)

            # fail safe if the generator does not work as expected
            any_missing = False
            for suffix in ['.h', '.cxx', 'Plugin.h', 'Plugin.cxx', 'Support.h', 'Support.cxx']:
                filename = os.path.join(output_path, msg_name + suffix)
                if not os.path.exists(filename):
                    any_missing = True
                    break
            if not any_missing:
                break
            print("'%s' failed to generate the expected files for '%s/%s'" %
                  (idl_pp, pkg_name, msg_name), file=sys.stderr)
            if count < max_count:
                count += 1
                print('Running code generator again (retry %d of %d)...' %
                      (count, max_count), file=sys.stderr)
                continue
            raise RuntimeError('failed to generate the expected files')

        if os.name != 'nt':
            # modify generated code to avoid unsed global variable warning
            # which can't be suppressed non-globally with gcc
            msg_filename = os.path.join(output_path, msg_name + '.h')
            _modify(msg_filename, pkg_name, msg_name, _inject_unused_attribute)

    return 0


def _inject_unused_attribute(pkg_name, msg_name, lines):
    # prepend attribute before constants of string type
    prefix = 'static const DDS_Char * Constants__'
    inject_prefix = '__attribute__((unused)) '
    for index, line in enumerate(lines):
        if not line.lstrip().startswith(prefix):
            continue
        lines[index] = line.replace(prefix, inject_prefix + prefix)
    return True


def _modify(filename, pkg_name, msg_name, callback):
    with open(filename, 'r') as h:
        lines = h.read().split('\n')
    modified = callback(pkg_name, msg_name, lines)
    if modified:
        with open(filename, 'w') as h:
            h.write('\n'.join(lines))


def generate_cpp(arguments_file):
    mapping = {
        'idl__rosidl_typesupport_connext_cpp.hpp.em':
        '%s__rosidl_typesupport_connext_cpp.hpp',
        'idl__dds_connext__type_support.cpp.em':
        '%s__type_support.cpp'
    }
    generate_files(arguments_file, mapping)
    return 0
