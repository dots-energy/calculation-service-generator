import re
import sys

DEFAULT_VALUE = "DEFAULT_VALUE"

SNAKE_CASE_FORMAT = "snake_case"
VERSION_FORMAT = "version"

REGEXES: dict = {
    SNAKE_CASE_FORMAT: r"[a-z0-9]+(_[a-z0-9]+)*",
    VERSION_FORMAT: r"^(\d+\.)?(\d+\.)?(\*|\d+)$",
}

REQUIRED_INPUTS: dict = {
    "service_name": SNAKE_CASE_FORMAT,
    "version": VERSION_FORMAT,
    "calculations": None,
}

VAR_TYPES: list = [
    "int",
    "float",
    "str",
    "bool",
    "dict",
    "List[int]",
    "List[str]",
    "List[bool]",
    "List[float]",
    "List[List[float]]",
]

DATA_NAMES_NOT_ALLOWED: list = ["model_parameters", "new_step", "simulation_done"]

input_dict: dict = dict({{cookiecutter | dictsort}})


def validate_string(input_string: str, formatting: str):
    if not re.fullmatch(REGEXES[formatting], input_string):
        print("ERROR: '%s' is not in '%s' format!" % (input_string, formatting))
        sys.exit(1)


def validate_data_variable(var_key_input: str, var_type_input: str):
    validate_string(var_key_input, SNAKE_CASE_FORMAT)
    if var_type_input not in VAR_TYPES:
        print(
            "ERROR: for '%s', '%s' is not one of the allowed variable types (%s)"
            % (var_key_input, var_type_input, VAR_TYPES)
        )
        sys.exit(1)


def validate_data_name(name: str):
    if name in DATA_NAMES_NOT_ALLOWED:
        print("ERROR: the data name '%s' is not allowed!" % name)
        sys.exit(1)


# validate required inputs
for req_key, req_format in REQUIRED_INPUTS.items():
    #  check if present:
    if input_dict[req_key] == DEFAULT_VALUE:
        print("ERROR: required input '%s' is not present" % req_key)
        sys.exit(1)
    #  check format
    if req_format:
        validate_string(input_dict[req_key], req_format)

# validate 'service config'
# for var_key, var_type in input_dict['service_config'].items():
#     validate_data_variable(var_key, var_type)

input_data_classes = []
output_data_class_names = []
for calc_name, calc_data in input_dict["calculations"].items():
    validate_string(calc_name, SNAKE_CASE_FORMAT)
    # validate 'receives' data classes
    if calc_data["receives"]:
        for service_name, service_data in calc_data["receives"].items():
            validate_string(service_name, SNAKE_CASE_FORMAT)
            for input_data_name, data_vars in service_data.items():
                validate_string(input_data_name, SNAKE_CASE_FORMAT)
                validate_data_name(input_data_name)
                input_data_classes.append(
                    {input_data_name: {"variables": data_vars, "service": service_name}}
                )
                for var_key, var_type in data_vars.items():
                    validate_data_variable(var_key, var_type)
    # validate 'sends' data classes
    if calc_data["sends"]:
        for output_data_name, data_vars in calc_data["sends"].items():
            validate_string(output_data_name, SNAKE_CASE_FORMAT)
            validate_data_name(output_data_name)
            output_data_class_names.append(output_data_name)
            for var_key, var_type in data_vars.items():
                validate_data_variable(var_key, var_type)

# check for duplicate input data class names: allowed, but only if variables and service_name are the same:
checked_input_data_classes = {}
for input_data_class in input_data_classes:
    data_name = next(iter(input_data_class))
    if data_name in output_data_class_names:
        print(
            "ERROR: data name ('%s') used for both input and output data, should be different!"
            % data_name
        )
        sys.exit(1)
    if data_name in checked_input_data_classes:
        data = input_data_class[data_name]
        duplicate_data = checked_input_data_classes[data_name]
        if not data["variables"] == duplicate_data["variables"]:
            print(
                f"ERROR: duplicate input data ({data_name}) found with different variables:\n'{data['variables']}]''"
                f" vs '{duplicate_data['variables']}'"
            )
            sys.exit(1)
        if not data["service"] == duplicate_data["service"]:
            print(
                "ERROR: duplicate input data found with ('%s') different service names:\n'%s' and '%s'"
                % (data_name, data["service"], duplicate_data["service"])
            )
            sys.exit(1)
    else:
        checked_input_data_classes[data_name] = input_data_class[data_name]

# check duplicate output data class names:
if len(output_data_class_names) > len(set(output_data_class_names)):
    dupes = [
        io_class_name
        for i, io_class_name in enumerate(output_data_class_names)
        if io_class_name in output_data_class_names[:i]
    ]
    print(
        "ERROR: the data objects should have unique names: '%s' is used more than once."
        % dupes[0]
    )
