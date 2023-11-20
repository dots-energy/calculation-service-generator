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

{% import 'jinja2-templates/input_data_inventory.jinja2' as input_data_inventory_j2 %}
from threading import Lock
from typing import Optional, Type
from model.io.log import LOCAL_LOGGER

from model.io.io_data import *


class InputDataInventory:
    def __init__(self):
        self.lock = Lock()

        # required data class types per calculation
        self.calcs_input_classes: dict = {{input_data_inventory_j2.input_class_names(cookiecutter)}}

        # expected ESDL objects (id's), per calculation service (identified by main topic) providing input
        self.expected_esdl_ids_dict: Optional[dict[str, List[EsdlId]]] = None

        # input_data dict with a list of IODataInterface instances per IO_class
        self.input_data_dict: dict = {}
        self.delete_all_received_input_data()

        # keep track of which calculations are done
        self.calcs_done = []
        self.calc_names_all_received = []

    # reset input_data_dict to empty lists for each data type, and reset calcs_done
    def delete_all_received_input_data(self):
        self.lock.acquire()
        LOCAL_LOGGER.debug("Removing all input data...")
        for calc_name, calc_input_classes in self.calcs_input_classes.items():
            for input_class in calc_input_classes:
                if input_class.get_name:
                    self.input_data_dict[input_class.get_name()] = []
        self.calcs_done = []
        self.calc_names_all_received = []
        LOCAL_LOGGER.debug("All input data removed!")
        self.lock.release()

    def set_expected_esdl_ids_for_input_data(self, connected_input_esdl_objects_dict: dict):
        # add lifecyle main topic for NewStep
        self.expected_esdl_ids_dict = {'/lifecycle/dots-so/model': ['dots-so']}

        for _, connected_input_esdl_objects in connected_input_esdl_objects_dict.items():
            for service_name, esdl_ids in connected_input_esdl_objects.items():
                for esdl_id in esdl_ids:
                    if f'/data/{service_name}/model' not in self.expected_esdl_ids_dict:
                        self.expected_esdl_ids_dict[f'/data/{service_name}/model'] = [esdl_id]
                    elif esdl_id not in self.expected_esdl_ids_dict[f'/data/{service_name}/model']:
                        self.expected_esdl_ids_dict[f'/data/{service_name}/model'].append(esdl_id)
        LOCAL_LOGGER.debug(
            f" set expecting input ESDL objects for '{{ cookiecutter.service_name }}': {self.expected_esdl_ids_dict}")

    # add input data and return a list of calculation names that have received all required input objects
    def add_input(self, main_topic: str, data_name: str, serialized_values: bytes) -> List[str]:
        # lock data_inventory to avoid simultaneous editing and consequent problems with checking if all required input
        # data is present
        self.lock.acquire()

        # create a new IODataInterface instance from received data and add to input_data_dict
        input_class_instance = self._find_and_create_class(main_topic, data_name, serialized_values)

        if input_class_instance:
            if not isinstance(input_class_instance, ModelParameters) and not self.expected_esdl_ids_dict:
                raise IOError("Input data received before model parameters were set")

            self.input_data_dict[data_name].append(input_class_instance)
            LOCAL_LOGGER.debug(
                f" added '{data_name}' data for service '{{ cookiecutter.service_name }}': {input_class_instance.get_variable_descr()}")

        # per calc, check if all input data is present
        non_executed_calc_names_input_received = self._get_calcs_with_all_input_received()

        self.lock.release()
        # return list of calc names that have received all required input data
        return non_executed_calc_names_input_received

    # for a specific calculation, get the needed input data:
    def get_input_data(self, calc_name: str) -> dict[str, List[IODataInterface]]:
        input_data = {}
        for data_class in self.calcs_input_classes[calc_name]:
            if data_class.get_name() == 'new_step':
                input_data['new_step'] = self.input_data_dict[data_class.get_name()][0]
            else:
                input_data[data_class.get_name() + '_list'] = self.input_data_dict[data_class.get_name()]
        return input_data

    def is_step_active(self) -> bool:
        return self.input_data_dict["new_step"] != {} and self.input_data_dict["new_step"] != None

    def _find_and_create_class(self, main_topic: str, data_name: str, serialized_values: bytes) -> IODataInterface:
        input_class_instance = None  # avoid multiple adding (input can be used by multiple calculations)

        for calc_name, calc_input_classes in self.calcs_input_classes.items():
            for input_class in calc_input_classes:
                if input_class.get_main_topic() == main_topic and input_class.get_name() == data_name \
                        and not input_class_instance:  # avoid multiple adding (multiple calculations can use input)
                    input_class_instance = self.create_new_class(input_class, serialized_values)

        if not input_class_instance:
            LOCAL_LOGGER.debug(f"No data class could be found for topic '{main_topic}', data name '{data_name}'.")

        return input_class_instance

    def create_new_class(self, input_class: Type[IODataInterface], serialized_values: bytes) -> IODataInterface:
        try:
            input_data_class = input_class()
            if len(serialized_values) > 0:
                input_data_class.set_values_from_serialized_protobuf(serialized_values)
            return input_data_class
        except TypeError:
            self.lock.release()
            raise IOError(
                f"The data class '{input_class.get_name()}' does not have the correct variables."
                f"\nVariables required: {input_class.get_variable_descr()}")

    def _get_new_calcs_with_all_input_received(self) -> List[str]:
        return_val = []
        for calc_name, calc_input_classes in self.calcs_input_classes.items():
            if calc_name not in self.calcs_done:  # check if all input available per calculation
                all_received = True
                for input_class in calc_input_classes:  # check if all input available per input data class
                    nr_of_data_class_objects_received = len(self.input_data_dict[input_class.get_name()])
                    if input_class.get_main_topic() in self.expected_esdl_ids_dict:
                        nr_of_data_class_objects_expected = len(
                            self.expected_esdl_ids_dict[input_class.get_main_topic()])
                    else:
                        nr_of_data_class_objects_expected = 0

                    if nr_of_data_class_objects_received < nr_of_data_class_objects_expected:
                        all_received = False

                if all_received and calc_name not in self.calc_names_all_received:
                    self.calc_names_all_received.append(calc_name)
                    return_val.append(calc_name)
        return return_val

    def set_calc_done(self, calc_name : str):
        self.lock.acquire()
        self.calcs_done.append(calc_name)
        self.lock.release()

    def all_calcs_done(self):
        return len(self.calcs_done) == len(self.calcs_input_classes)
