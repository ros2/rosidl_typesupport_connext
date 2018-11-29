# Copyright 2018 Open Source Robotics Foundation, Inc.
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
import re


def convert_to_connext_idl(input_idl_file_path, output_basepath):
    """
    Convert a generic IDL file to a new IDL file compatible with RTI Connext.
    The new IDL file is created with the same base name as the input file.
    A file with the same name in the output path wil be overwritten.
    :param: input_idl_file_path The path to the input IDL file.
    :param: output_basepath The output path where the new IDL file is written.
    """
    # Get two level of parent folders for idl file
    folder = os.path.dirname(input_idl_file_path)
    parent_folder = os.path.dirname(folder)
    output_idl_file_path = os.path.join(
        output_basepath,
        os.path.basename(parent_folder),
        os.path.basename(folder),
        os.path.basename(input_idl_file_path)
    )
    try:
        os.makedirs(os.path.dirname(output_idl_file_path))
    except FileExistsError:
        pass

    # Regexes for find and replace
    regex_substitutions = []
    # Replace unsupported types
    regex_substitutions.append((re.compile(r'([<>,\s])int8([<>,\s])'), r'\1octet\2'))
    regex_substitutions.append((re.compile(r'([<>,\s])uint8([<>,\s])'), r'\1octet\2'))
    regex_substitutions.append((re.compile(r'([<>,\s])int16([<>,\s])'), r'\1short\2'))
    regex_substitutions.append((re.compile(r'([<>,\s])uint16([<>,\s])'), r'\1unsigned short\2'))
    regex_substitutions.append((re.compile(r'([<>,\s])int32([<>,\s])'), r'\1long\2'))
    regex_substitutions.append((re.compile(r'([<>,\s])uint32([<>,\s])'), r'\1unsigned long\2'))
    regex_substitutions.append((re.compile(r'([<>,\s])int64([<>,\s])'), r'\1long long\2'))
    regex_substitutions.append((re.compile(r'([<>,\s])uint64([<>,\s])'), r'\1unsigned long long\2'))
    with open(output_idl_file_path, 'w') as output_idl:
        with open(input_idl_file_path, 'r') as input_idl:
            for line in input_idl:
                # Replace unsupported types
                for regex, substitution in regex_substitutions:
                    line = regex.sub(substitution, line)
                output_idl.write(line)
    return output_idl_file_path
