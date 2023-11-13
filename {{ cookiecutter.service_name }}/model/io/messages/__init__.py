#  This work is based on original code developed and copyrighted by TNO 2023.
#  Subsequent contributions are licensed to you by the developers of such code and are
#  made available to the Project under one or several contributor license agreements.
#
#  This work is licensed to you under the Apache License, Version 2.0.
#  You may obtain a copy of the license at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Contributors:
#      TNO         - Initial implementation
#  Manager:
#      TNO

from model.io.messages.lifecycle_pb2 import (
    EnvironmentVariable,
    ModelConfiguration,
    DeployModels,
    ReadyForProcessing,
    ModelsReady,
    ModelParameters,
    Parameterized,
    NewStep,
    CalculationsDone,
    ErrorOccurred,
    SimulationDone,
    UnhealthyModelStatus,
    UnhealthyModel,
    TerminationStatus,
    ModelHasTerminated,
    AllModelsHaveTerminated,
)
from model.io.messages.io_data_pb2 import *
