#!/bin/bash

echo Starting MQTT broker...
mosquitto/run_mosquitto.sh;

echo Starting fake simulation orchestrator...
cd ..
source venv/bin/activate
python3 -m test_local.fake_simulation_orchestrator
