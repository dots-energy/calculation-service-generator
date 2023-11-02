@ECHO OFF

echo Starting MQTT broker...
call mosquitto\run_mosquitto.bat

:label
curl.exe https://localhost:1883 >NUL 2>&1
if %ERRORLEVEL% LEQ 7 (
   echo "waiting for mqtt broker to be up"
   timeout 3
   GOTO label
)

echo Starting fake simulation orchestrator...
cd ..
call venv\Scripts\activate
python -m test_local.fake_simulation_orchestrator
