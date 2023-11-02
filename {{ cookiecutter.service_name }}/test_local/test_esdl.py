# Create an energy system
{% import 'jinja2-templates/test_esdl.jinja2' as test_esdl_j2 %}
import uuid
from typing import List

from model.types import EsdlId
from esdl import *
from pyecore.resources import ResourceSet, URI
from pyecore.ecore import EObject


def create_test_esdl_file(file_name: str, esdl_id: EsdlId, example_assets: List[type(EObject)]):
    energy_system = EnergySystem(name="Nederland ES", id=str(uuid.uuid4()))
    energy_system_instance = Instance(name="NL", id=str(uuid.uuid4()))

    # Instantiate the created energy system; there can be one or more instances of the same energy system
    energy_system_instance.aggrType = AggrTypeEnum.PER_COMMODITY
    energy_system.instance.append(energy_system_instance)

    # Every energy system has an area
    energy_system.instance[0].area = Area(
        name="Municipality area", id=str(uuid.uuid4())
    )

    model_asset = PVInstallation(name="pv installation 1", id=esdl_id)
    energy_system.instance[0].area.asset.append(model_asset)

    nr_of_connected_input_services = {{ test_esdl_j2.nr_of_input_services(cookiecutter) }}
    for iService in range(nr_of_connected_input_services):
        asset_class = globals()[example_assets[iService]]
        connected_asset = asset_class(
            name=example_assets[iService], id=str(uuid.uuid4())
        )
        # connected_asset = esdl.PVPanel(name="PV panel", id=str(uuid.uuid4()))
        energy_system.instance[0].area.asset.append(connected_asset)
        out_port = OutPort(id=str(uuid.uuid4()))
        connected_asset.port.append(out_port)
        in_port = InPort(id=str(uuid.uuid4()), connectedTo=[out_port])
        model_asset.port.append(in_port)

    rset = ResourceSet()
    resource = rset.create_resource(URI(file_name))
    resource.append(energy_system)
    resource.save()

    print(f"Test ESDL file created: '{file_name}'")
