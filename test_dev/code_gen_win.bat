docker run --rm -v ${PWD}/test_service_configs/test1_battery_service.yaml:/usr/src/app/input/config.yaml -v ${PWD}:/usr/src/app/output calculation-service-generator