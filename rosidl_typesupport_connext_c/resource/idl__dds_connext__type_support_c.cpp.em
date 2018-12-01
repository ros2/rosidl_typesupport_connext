// generated from rosidl_typesupport_connext_c/resource/idl__dds_connext__type_support_c.cpp.em
// with input from @(package_name):@(interface_path)
// generated code does not contain a copyright notice

@{
#######################################################################
# EmPy template for generating <idl>__type_support_c.cpp files
#
# Context:
#  - package_name (string)
#  - content (rosidl_parser.definition.IdlContent result of parsing IDL file)
#  - interface_path (Path relative to the directory named after the package)
#######################################################################
include_directives = set()
#######################################################################
# Handle message
#######################################################################
from rosidl_parser.definition import Message
for message in content.get_elements_of_type(Message):
    TEMPLATE(
        'msg__type_support_c.cpp.em',
        package_name=package_name, interface_path=interface_path,
        message=message, include_prefix=message.structure.type.name,
        include_directives=include_directives
    )
#######################################################################
# Handle service
#######################################################################
from rosidl_parser.definition import Service
for service in content.get_elements_of_type(Service):
    TEMPLATE(
        'srv__type_support_c.cpp.em',
        package_name=package_name, interface_path=interface_path,
        service=service, include_prefix=service.structure_type.name,
        include_directives=include_directives
    )
#######################################################################
# Handle action
#######################################################################
from rosidl_parser.definition import Action
for action in content.get_elements_of_type(Action):
    TEMPLATE(
        'srv__type_support_c.cpp.em',
        package_name=package_name, interface_path=interface_path,
        service=action.goal_service,
        include_prefix=action.goal_service.structure_type.name,
        include_directives=include_directives
    )
    TEMPLATE(
        'srv__type_support_c.cpp.em',
        package_name=package_name, interface_path=interface_path,
        service=action.result_service,
        include_prefix=action.result_service.structure_type.name,
        include_directives=include_directives
    )
    TEMPLATE(
        'msg__type_support_c.cpp.em',
        package_name=package_name, interface_path=interface_path,
        message=action.feedback_message,
        include_prefix=action.feedback_message.structure.type.name,
        include_directives=include_directives
    )
}@
