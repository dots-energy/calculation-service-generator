# Calculation Service Generator

The calculation service generator is based on the open source
[**cookiecutter**](https://github.com/cookiecutter/cookiecutter),
[**protobuf**](https://github.com/protocolbuffers/protobuf) and [**black**](https://github.com/psf/black) libraries.
It generates, compiles and lints a boilerplate MCS calculation service project.  
On the [MCS wiki](https://ci.tno.nl/gitlab/groups/dots/-/wikis/home#create-calculation-services) you can find how the
calculation service generator is used.

## Repository Structure

The repository contains several folders with different purposes:

- **ci:** build and push the docker image.
- **hooks:** Contains the pre- and post-generation cookiecutter hooks.
- **test_dev:** Contains old testing stuff, can be ignored.
- **test:** The directory for unit tests. Currently empty as no unit tests were written (Please create tests...)
- **{{ cookiecutter.service_name }}:** Cookiecutter template folder, all of these files (except `.jinja2` files) will be
  put in the boilerplate project. For example: the `.dockerignore` and `.gitignore` files in this folder will be used
  in the boilerplate project and not for this project (then the files in the root of this project will be used).
- **{{ cookiecutter.service_name }}/deploy:** Deploy scripts for the boilerplate project.
- **{{ cookiecutter.service_name }}/jinja2-templates:** Templating files used by cookiecutter. This folder will be
  deleted in the cookiecutter post generation phase.
- **{{ cookiecutter.service_name }}/message_definitions:** The protobuf message definitions for IO data and lifecycle
  to and from the Simulation Orchestrator. These files will be compiled to `_pb2.py` files and will be placed in the
  `model/io/messages` folder.
- **{{ cookiecutter.service_name }}/model:** Modelling code for the boilerplate project. The
  `model/calculation/service_calc.py` file contains the calculation functions which need to be filled with logic.
- **{{ cookiecutter.service_name }}/test_local:** Files needed for local testing of the calculation service.
- **.dockerignore:** A file containing which files and directories to ignore when submitting this repo as a Docker
  build context. In other words, it prevents the entries from being sent to Docker when the Docker image is build.
- **.gitignore:** A file containing which files and directories not to add to the git repository.
- **.gitlab-ci.yml:** The steps executed by the Gitlab CI pipeline when a new commit is pushed to the git repository:
  a docker image is created when merging to main ('latest') and when pushing a git tag ('tag name').
- **build.sh:** Script that will be executed when creating a boilerplate projects. It runs cookiecutter, compiles
  the protobuf messages and lints the code.
- **cookiecutter.json:** Configuration file needed for cookiecutter, filled with default values since we always use the
  yaml input option.
- **cookiecutter_service_config.yaml:** Example configuration file
- **Dockerfile:** The build file for the Docker image.
- **requirements.txt:** The Python dependencies necessary to run the code to create a boilerplate project.

## Development and testing

Install requirements.txt in a Python 3.9 environment.
To test the code a boilerplate project needs to be created which can subsequently be tested.
This can be done by running the code in a docker container as described in
[MCS wiki](https://ci.tno.nl/gitlab/groups/dots/-/wikis/home#create-boiler-plate-service). This also contains a
description and example of the needed configuration `.yaml` file.
For this the code needs to build and pushed to a docker image.

### Build and push image

Before usage an image needs to be pushed by running the script in the `ci` folder.

### Testing during development

A quicker way to test during development is to run the separate commands from the command line: cookiecutter needs to be
run to create/update the project code, protobuf compile is used to create/update the protobuf`_pb2.py` messages.
Then do the local testing in the created/updated boilerplate project.

#### Cookiecutter

To create/update the code (interpret the jinja2 templating) run cookiecutter with a configuration file, from the
directory containing this repository, so one level up from the root folder:

````bash
cookiecutter calculation-service-generator --no-input --config-file cookiecutter_service_config.yaml -f
````

where  
`--no-input` suppresses the default prompt for parameters  
`--config-file <config_file.yaml>` user configuration file  
`-f` overwrite output directory if already exists

#### ProtoBuf messages

Download and install the [Protobuf Compiler](https://github.com/protocolbuffers/protobuf/releases/tag/v3.19.0-rc2)
To compile the protobuf messages, in the root folder of the newly created project, run:

```bash
protoc -I .\message_definitions\ --python_out .\model\io\messages\ .\message_definitions\*.proto
```
