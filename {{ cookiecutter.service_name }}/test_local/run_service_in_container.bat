@ECHO OFF

set VERSION=0.0.1

docker build -t {{ cookiecutter.service_name }}:%VERSION% ..

docker run --rm --env-file ..\.env.docker {{ cookiecutter.service_name }}:%VERSION%
