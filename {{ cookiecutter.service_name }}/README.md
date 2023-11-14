# {{ cookiecutter.service_name }}

This calculation service was created using the Dots Calculation Service Generator. More information on Dots can be found
in the [wiki](https://github.com/dots-energy/simulation-orchestrator/wiki).

## Development

Python version 3.9 is used, when using additional python libraries `requirements.txt` needs to be updated.

The code outside the `model\calculation` package should not have to be changed (except for
`test_local\start_test_simulation.py` for local testing).  
A calculation function for each calculation specified in `cookiecutter_service_config.yaml` can be found in:
`model\calculation\service_calc.py`.  
This ServiceCalc class has a constructor which is called on deployment of the service in a docker container on Azure.
Next the esdl file and `calculation_services` are received and processed in the `setup()` function.
Then each calculation function is run once per time step, when the required data has been received.

Logic should be implemented in these functions.

## Deployment

When the service is ready, a docker image of it should be pushed to a repository available to the Simulation
Orchestrator on Azure.
To build and push a docker image to dockerhub, login:  
`docker login -u dotsenergyframework`  
followed by:  
`deploy/build_and_push_image_dockerhub.sh`.   
The image is now available to use by Dots on a Azure or local kind cluster.

## Local testing

Fast local testing during development is possible without building and pushing the image each time, and without setting
up and using a kubernetes cluster.

To make this possible several components need to be mocked or run locally in docker desktop such as:

1. Mosquitto
2. InfluxDB
3. Grafana
4. Mock simulation orchestrator
5. Mock required data sending
6. Use test EDSL file
7. Start this calculation service from `main.py` or in a docker container

Three steps are needed to create all of the above which are explained below.

### Start Mosquitto, InfluxDB and Grafana (1,2,3)

Terminal 1 at `<repo root>\test_local` (docker must be running):

```bash
start_local_infrastructure.bat (Windows)  
start_local_infrastructure.sh (Unix)
```

### Start test simulation with test ESDL file and send required input data (4,5,6)

Run `start_test_simulation.py` in your IDE to mimic the simulation orchestrator.

This test simulation will wait for an MQTT message that the service has started up, after which it will start the
simulation flow by sending the necessary configuration data. Then the time steps sequence starts with 'NewStep' messages
and the required input data.

### Start the calculation service (7)

Create two .env files for running from `main.py` directly and running inside a docker container.  
Terminal 2 at `<repo root>`:

```
copy .env.template .env.docker
copy .env.template .env
```

In the `.env` file set `MQTT_HOST=localhost` and `INFLUXDB_HOST=localhost`

Run `main.py` in the IDE,  
Or alternatively, to also test the the container setup, including python libraries in requirements.txt:  
Terminal 2 at `<repo root>\test_local` (docker must be running):

```
run_service_in_container.bat (Windows)
run_service_in_container.sh (Unix)
```

### Expected output

In the `main.py` output console (or terminal 2 when running the service in a docker container) you should see something
like this:

```console
(venv) PS C:\Users\vrijlandtmaw\code\dots\test-services\service_name\test> .\run_service_in_container.bat
[+] Building 23.9s (11/11) FINISHED
 => [internal] load build definition from Dockerfile                                                                                                                      0.0s 
 => => transferring dockerfile: 32B                                                                                                                                       0.0s 
 => [internal] load .dockerignore                                                                                                                                         0.0s 
 => => transferring context: 2B                                                                                                                                           0.0s 
 => [internal] load metadata for docker.io/library/python:3.9-slim                                                                                                        0.6s 
 => [internal] load build context                                                                                                                                         0.5s 
 => => transferring context: 316.54kB                                                                                                                                     0.5s 
 => [1/6] FROM docker.io/library/python:3.9-slim@sha256:5192f07402cbe8b0267eef13085b321d50ab8aaac79d2f0657f96810c3f4555c                                                  0.0s 
 => CACHED [2/6] RUN mkdir /app/                                                                                                                                          0.0s 
 => CACHED [3/6] WORKDIR /app                                                                                                                                             0.0s 
 => [4/6] COPY . .                                                                                                                                                        0.5s 
 => [5/6] COPY requirements.txt ./                                                                                                                                        0.1s 
 => [6/6] RUN pip install -r requirements.txt                                                                                                                            20.2s 
 => exporting to image                                                                                                                                                    1.8s 
 => => exporting layers                                                                                                                                                   1.7s 
 => => writing image sha256:ac45eb7c8a3fc64c522328c60d1fdbaee1270987585a22b6f4f60052fc25f6aa                                                                              0.0s 
 => => naming to docker.io/library/service_name:0.0.1                                                                                                                     0.0s 

Use 'docker scan' to run Snyk tests against images to find vulnerabilities and learn how to fix them
03/28/2023 12:38:08 PM [MainThread][main.py:32][local-logger-INFO]: Config:
03/28/2023 12:38:08 PM [MainThread][main.py:39][local-logger-INFO]:     SIMULATION_ID:       test-simulation-5omdi245
03/28/2023 12:38:08 PM [MainThread][main.py:39][local-logger-INFO]:     MODEL_ID:            pv-panel_model1
03/28/2023 12:38:08 PM [MainThread][main.py:39][local-logger-INFO]:     MQTT_HOST:           host.docker.internal
03/28/2023 12:38:08 PM [MainThread][main.py:39][local-logger-INFO]:     MQTT_PORT:           1883
03/28/2023 12:38:08 PM [MainThread][main.py:39][local-logger-INFO]:     MQTT_QOS:            0
03/28/2023 12:38:08 PM [MainThread][main.py:39][local-logger-INFO]:     MQTT_USERNAME:       dots
03/28/2023 12:38:08 PM [MainThread][main.py:39][local-logger-INFO]:     MQTT_PASSWORD:       <hidden>
03/28/2023 12:38:08 PM [MainThread][main.py:39][local-logger-INFO]:     INFLUXDB_HOST:       host.docker.internal
03/28/2023 12:38:08 PM [MainThread][main.py:39][local-logger-INFO]:     INFLUXDB_PORT:       8086
03/28/2023 12:38:08 PM [MainThread][main.py:39][local-logger-INFO]:     INFLUXDB_USER:       admin
03/28/2023 12:38:08 PM [MainThread][main.py:39][local-logger-INFO]:     INFLUXDB_PASSWORD:   <hidden>
03/28/2023 12:38:08 PM [MainThread][main.py:39][local-logger-INFO]:     INFLUXDB_NAME:       GO-e
03/28/2023 12:38:08 PM [MainThread][main.py:43][local-logger-INFO]:
03/28/2023 12:38:10 PM [Thread-3][service_calc.py:146][local-logger-INFO]: calculation 'calc2' started
03/28/2023 12:38:10 PM [Thread-3][service_calc.py:165][local-logger-WARNING]: input_data3_list for ESDL 'e1b3dc89-cee8-4f8e-81ce-a0cb6726c17e': [] 
03/28/2023 12:38:10 PM [Thread-3][service_calc.py:186][local-logger-INFO]: calculation 'calc2' finished
03/28/2023 12:38:11 PM [Thread-4][service_calc.py:99][local-logger-INFO]: calculation 'calc1' started
03/28/2023 12:38:11 PM [Thread-4][service_calc.py:137][local-logger-INFO]: calculation 'calc1' finished
03/28/2023 12:38:12 PM [Thread-6][service_calc.py:146][local-logger-INFO]: calculation 'calc2' started
03/28/2023 12:38:12 PM [Thread-6][service_calc.py:165][local-logger-WARNING]: input_data3_list for ESDL 'e1b3dc89-cee8-4f8e-81ce-a0cb6726c17e': [] 
03/28/2023 12:38:12 PM [Thread-6][service_calc.py:186][local-logger-INFO]: calculation 'calc2' finished
03/28/2023 12:38:13 PM [Thread-7][service_calc.py:99][local-logger-INFO]: calculation 'calc1' started
03/28/2023 12:38:13 PM [Thread-7][service_calc.py:137][local-logger-INFO]: calculation 'calc1' finished
03/28/2023 12:38:14 PM [Thread-9][service_calc.py:146][local-logger-INFO]: calculation 'calc2' started
03/28/2023 12:38:14 PM [Thread-9][service_calc.py:165][local-logger-WARNING]: input_data3_list for ESDL 'e1b3dc89-cee8-4f8e-81ce-a0cb6726c17e': []
03/28/2023 12:38:14 PM [Thread-9][service_calc.py:186][local-logger-INFO]: calculation 'calc2' finished
03/28/2023 12:38:15 PM [Thread-10][service_calc.py:99][local-logger-INFO]: calculation 'calc1' started
03/28/2023 12:38:15 PM [Thread-10][service_calc.py:137][local-logger-INFO]: calculation 'calc1' finished
03/28/2023 12:38:15 PM [Thread-11][influxdb_connector.py:171][local-logger-INFO]: InfluxDB writing 4 points to measurement 'econnection' with tag simulationRun test-simulation-5omdi245
03/28/2023 12:38:15 PM [Thread-11][mqtt_client.py:82][sim-logger-INFO]: Simulation Orchestrator terminated service: 'service_name: pv-panel_model1' - 'test-simulation-5omdi245'
03/28/2023 12:38:16 PM [MainThread][main.py:52][local-logger-INFO]: Service 'service_name: pv-panel_model1' terminated

```
