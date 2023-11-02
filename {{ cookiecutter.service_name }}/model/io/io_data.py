#!/usr/bin/env python
{% import 'jinja2-templates/io_data.jinja2' as io_data_j2 %}
from overrides import EnforceOverrides, overrides
from typing import List
import json
from model.types import EsdlId
import model.io.messages as messages


class IODataInterface(EnforceOverrides):
    def set_values_from_serialized_protobuf(self, serialized_message: bytes):
        """Set values from protobuf message"""
        pass

    def get_values_as_serialized_protobuf(self) -> bytes:
        """Get dictionary with all variables"""
        pass

    @classmethod
    def get_name(cls) -> str:
        """Get data name"""
        pass

    @classmethod
    def get_main_topic(cls) -> str:
        """Get MQTT topic"""
        pass

    @classmethod
    def get_variable_descr(cls) -> str:
        """"Get variables description"""
        pass


class ModelParameters(IODataInterface):
    def __init__(self, parameters_dict: dict = None):
        self.parameters_dict: dict = parameters_dict

    @overrides
    def set_values_from_serialized_protobuf(self, serialized_message: bytes):
        config_data = messages.ModelParameters()
        config_data.ParseFromString(serialized_message)
        self.parameters_dict = json.loads(config_data.parameters_dict)

    @overrides
    def get_values_as_serialized_protobuf(self) -> bytes:
        protobuf_message = messages.ModelParameters()
        protobuf_message.parameters_dict = json.dumps(self.parameters_dict)
        return protobuf_message.SerializeToString()

    @classmethod
    @overrides
    def get_name(cls) -> str:
        return "model_parameters"

    @classmethod
    @overrides
    def get_main_topic(cls) -> str:
        return '/lifecycle/dots-so/model'

    @classmethod
    @overrides
    def get_variable_descr(cls) -> str:
        return "{parameters_dict': 'dict'}"


class NewStep(IODataInterface):
    def __init__(self, parameters_dict: dict = None):
        self.parameters_dict: dict = parameters_dict

    @overrides
    def set_values_from_serialized_protobuf(self, serialized_message: bytes):
        config_data = messages.NewStep()
        config_data.ParseFromString(serialized_message)
        self.parameters_dict = json.loads(config_data.parameters_dict)

    @overrides
    def get_values_as_serialized_protobuf(self) -> bytes:
        protobuf_message = messages.NewStep()
        protobuf_message.parameters_dict = json.dumps(self.parameters_dict)
        return protobuf_message.SerializeToString()

    @classmethod
    @overrides
    def get_name(cls) -> str:
        return "new_step"

    @classmethod
    @overrides
    def get_main_topic(cls) -> str:
        return '/lifecycle/dots-so/model'

    @classmethod
    @overrides
    def get_variable_descr(cls) -> str:
        return "{'parameters_dict': 'dict'}"


{{- io_data_j2.input_classes(cookiecutter)}}
{{- io_data_j2.output_classes(cookiecutter)}}
